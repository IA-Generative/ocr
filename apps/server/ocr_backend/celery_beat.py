"""Entrypoint for the Celery Beat scheduler process.

Run as: `celery -A ocr_backend.celery_beat:celery_app beat`.

Importing `.purge` registers the `purge_old_tasks` task and its beat schedule entry
on `celery_app` as a side effect; `celery beat` only needs this module to know what
to schedule, it never executes the task itself (a worker subscribed to the queue does).
"""

from src.connector.broker_connector import celery_app

from . import purge  # noqa: F401

PURGE_QUEUE = "purge"

# The OCR workers consume the default queue on this same broker and do not register the
# purge task, and this process does not register the OCR task. Sharing the default queue
# would have each side discard the other's messages as unregistered tasks (half of the OCR
# jobs vanish). Moving this process onto its own queue sends the purge task there and makes
# the worker started from this module consume only that queue.
celery_app.conf.task_default_queue = PURGE_QUEUE

__all__ = ["PURGE_QUEUE", "celery_app"]
