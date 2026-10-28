import multiprocessing
import os

# Silences third-party CLI/progress-bar noise (paddle glog, huggingface_hub,
# tqdm) so pod output stays parseable. Must be set BEFORE the first import of
# paddle/huggingface_hub/tqdm; setdefault so an explicit chart override wins.
for _env_key, _env_value in (
    ("GLOG_minloglevel", "2"),
    ("HF_HUB_DISABLE_PROGRESS_BARS", "1"),
    ("TQDM_DISABLE", "1"),
):
    os.environ.setdefault(_env_key, _env_value)

# PP-OCRv5 (PaddleX 3.x) uses multiprocessing.Pool internally during predict().
# On Linux, the default start method "fork" corrupts PaddlePaddle's BLAS/inference
# engine state after fork → deadlock or silent crash.
# Must be set BEFORE any PaddlePaddle/PaddleX import.
multiprocessing.set_start_method("spawn", force=True)  # noqa: E402

import json  # noqa: E402
import traceback  # noqa: E402

import sentry_sdk  # noqa: E402
from sentry_sdk.integrations.celery import CeleryIntegration  # noqa: E402

from services.base.pipeline import Pipeline  # noqa: E402
from src.config import SentrySettings  # noqa: E402
from src.connector.broker_connector import celery_app, celery_config  # noqa: E402
from src.logger import logger  # noqa: E402
from src.schemas.task import TaskForm, TaskModel, TaskStatus, task_table  # noqa: E402
from services.base.tracing import get_tracing_service  # noqa: E402
from celery.signals import worker_process_init  # noqa: E402

_sentry_settings = SentrySettings()
if _sentry_settings.SENTRY_WORKER_DSN:
    try:
        sentry_sdk.init(
            dsn=_sentry_settings.SENTRY_WORKER_DSN,
            send_default_pii=_sentry_settings.SEND_DEFAULT_PII,
            environment=os.getenv("ENVIRONMENT", "production"),
            integrations=[CeleryIntegration()],
        )
    except Exception as e:
        logger.warning(f"Sentry initialization failed, continuing without it: {e}")

process_ocr: Pipeline | None = None


@worker_process_init.connect
def init_worker(**kwargs):
    """Initialise le pipeline OCR après que le process worker Celery est prêt.

    Différer l'initialisation de PaddleOCR/PaddleX ici (plutôt qu'au module load)
    garantit que le start method "spawn" est actif et que le process est stable.
    """
    global process_ocr

    # PaddlePaddle/PaddleX initialise son pool de threads OpenMP à la PREMIÈRE
    # inférence (pas à l'import). Ces variables doivent donc être positionnées
    # AVANT l'import de PaddleX ET avant le premier appel à predict().
    # 1 thread = pas de fork interne → supprime le deadlock en contexte Celery solo.
    for _env_key in (
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "PADDLE_NUM_THREADS",
    ):
        os.environ[_env_key] = "1"
    # Flag interne PaddlePaddle pour le nombre de threads d'inférence CPU
    os.environ["FLAGS_paddle_num_threads"] = "1"

    logger.info(f"[worker_process_init] Chargement du pipeline {os.environ['PROCESS_NAME']}…")
    # Import différé : PaddlePaddle/PaddleX n'est importé qu'ici,
    # après que multiprocessing.set_start_method("spawn") est actif
    # et que le process Celery est pleinement initialisé.
    from .factory import load_worker  # noqa: PLC0415

    process_ocr = load_worker(name=os.environ["PROCESS_NAME"])
    logger.info("[worker_process_init] Pipeline prêt.")


logger.info(
    f"{os.environ['WORKER_NAME']} - {os.environ['PROCESS_NAME']} {celery_config.CELERY_APP_NAME}" + "\n" + 79 * "*"
)

tracing = get_tracing_service(tracing_name=os.environ.get("TRACING_SERVICE", "logging"))


@celery_app.task(name=os.environ["WORKER_NAME"], bind=True)
def launch_task(self, task_info: dict):
    task = TaskModel.model_validate(json.loads(task_info))
    with sentry_sdk.new_scope() as scope:
        scope.set_tag("task.id", task.id)
        scope.set_tag("worker.name", os.environ["WORKER_NAME"])
        scope.set_user({"id": task.user_id})
        return _run_task(task)


def _run_task(task: TaskModel) -> dict:
    global process_ocr
    if process_ocr is None:
        # Celery task_always_eager (tests) ne déclenche pas worker_process_init.
        # Initialisation lazy pour ce cas uniquement.
        logger.warning("[_run_task] process_ocr non initialisé, init lazy (contexte test ?)")
        from .factory import load_worker  # noqa: PLC0415

        process_ocr = load_worker(name=os.environ["PROCESS_NAME"])
    try:
        with tracing.trace_context(trace_id=task.id, user_id=task.user_id, name=os.environ["WORKER_NAME"]):
            task = process_ocr.process(task=task)

        return task.model_dump()
    except Exception as e:
        # `extras` is returned as-is by the tasks API: the stack trace stays in the logs.
        logger.error(f"[_run_task] task {task.id} failed: {e}\n{traceback.format_exc()}")
        task.extras = task.extras if task.extras else {}
        task.extras["error"] = str(e)
        task_table.update_task(
            task_id=task.id,
            form_data=TaskForm(
                user_id=task.user_id,
                type=task.type,
                status=TaskStatus.FAILED.value,
                extras=task.extras,
            ),
        )
        raise


if __name__ == "__main__":
    logger.info("Start to consume...")
    celery_app.start()
