import os

LAYOUT_WORKER_NAME = "worker.tasks.layout"
LAYOUT_QUEUE = "layout"
TABLE_WORKER_NAME = "worker.tasks.table"
TABLE_QUEUE = "table"
# Clé de `extras` du message envoyé au worker table : {"<index page>": [[xmin, ymin, xmax, ymax], ...]}
TABLE_REGIONS_KEY = "table_regions"

_LAYOUT_CONTENT_TYPES = ("application/pdf",)


def is_layout_content_type(content_type: str | None) -> bool:
    """Le layout ne s'applique qu'aux images et aux PDF."""
    if not content_type:
        return False
    return content_type.startswith("image/") or content_type in _LAYOUT_CONTENT_TYPES


def layout_enabled() -> bool:
    """Interrupteur côté API : à ``false`` quand aucun worker layout n'est déployé (sinon ``layout_status``
    resterait ``pending`` à jamais, la tâche attendant dans une queue sans consommateur)."""
    return os.environ.get("LAYOUT_ENABLED", "true").strip().lower() not in ("0", "false", "no", "off")
