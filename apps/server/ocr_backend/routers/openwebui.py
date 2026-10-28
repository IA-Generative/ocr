"""
Route compatible OpenWebUI ExternalDocumentLoader.

OpenWebUI appelle PUT /process avec :
  - Authorization: Bearer <OPENWEBUI_API_KEY>
  - Content-Type: <mime_type>
  - X-Filename: <url-encoded filename>
  - Body: bytes bruts du fichier

Réponse attendue :
  [{"page_content": "...", "metadata": {...}}, ...]

Référence : open-webui/retrieval/loaders/external_document.py
"""

import asyncio
import os
import secrets
from io import BytesIO
from typing import Annotated, Optional
from urllib.parse import unquote

from fastapi import APIRouter, Header, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from starlette.datastructures import Headers

from ocr_backend.core.security.token import RequestContext
from ocr_backend.routers.jobs import upload_file
from ocr_backend.routers.task import delete_task_by_id, get_task_by_id_user
from src.logger import logger
from src.schemas.task import TaskModel, TaskOperation, TaskStatus

openwebui_router = APIRouter(tags=["OpenWebUI"])

_OPENWEBUI_API_KEY: Optional[str] = os.environ.get("OPENWEBUI_API_KEY")
_OPENWEBUI_USER_ID: str = os.environ.get("OPENWEBUI_USER_ID", "openwebui")

_RESPONSES: dict[int | str, dict[str, str]] = {
    400: {"description": "Corps vide ou illisible"},
    401: {"description": "Clé API manquante ou invalide"},
    500: {"description": "Erreur pipeline OCR"},
    503: {"description": "OPENWEBUI_API_KEY non configurée"},
    504: {"description": "Timeout traitement"},
}


def _verify_api_key(authorization: Optional[str]) -> None:
    """Vérifie le header Authorization: Bearer <key>."""
    if not _OPENWEBUI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENWEBUI_API_KEY non configurée sur ce serveur.",
        )
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header Authorization manquant.",
        )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not secrets.compare_digest(token, _OPENWEBUI_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide.",
        )


def _build_pages_content(task: TaskModel, filename: str, mime_type: str, size_bytes: int) -> list:
    """Construit la réponse au format OpenWebUI."""
    if not task.output:
        return []
    docs = []
    for page in task.output.pages:
        text = task.output.set_page_text(page)
        docs.append(
            {
                "page_content": text,
                "metadata": {
                    "filename": filename,
                    "mime_type": mime_type,
                    "size_bytes": size_bytes,
                    "task_id": task.id,
                    "page": page.page,
                    "source": filename,
                },
            }
        )
    return docs


async def _cleanup_task(task_id: str, ctx: RequestContext) -> None:
    """Supprime la tâche et le fichier associé (S3) une fois la réponse construite. Best-effort."""
    try:
        await delete_task_by_id(task_id=task_id, ctx=ctx)
        logger.info(f"[OpenWebUI] Task {task_id} and associated file deleted")
    except Exception as e:
        logger.error(f"[OpenWebUI] Failed to cleanup task {task_id}: {e}")


async def _poll_task(task_id: str, ctx: RequestContext, max_wait_time: int, poll_interval: int) -> TaskModel:
    """Attend la completion de la tâche et retourne le TaskModel final."""
    elapsed = 0
    while elapsed < max_wait_time:
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
        try:
            task = await get_task_by_id_user(task_id, ctx=ctx)
        except Exception:
            continue

        if task.status == TaskStatus.COMPLETED.value:
            return task

        if task.status == TaskStatus.FAILED.value:
            error = (task.extras or {}).get("error", "Erreur inconnue")
            raise HTTPException(status_code=500, detail=f"Traitement échoué: {error}")

    raise HTTPException(
        status_code=504,
        detail=f"Timeout après {max_wait_time}s — tâche {task_id} non terminée.",
    )


@openwebui_router.put(
    "/process",
    summary="OpenWebUI — traitement de document",
    description=(
        "Endpoint compatible avec l'ExternalDocumentLoader d'OpenWebUI. "
        "Accepte un fichier en bytes bruts et retourne le texte extrait "
        "sous forme de liste de documents LangChain-compatible."
    ),
    response_description="Liste de documents {page_content, metadata}",
    responses=_RESPONSES,
)
async def openwebui_process_document(
    request: Request,
    authorization: Annotated[Optional[str], Header()] = None,
    x_filename: Annotated[Optional[str], Header()] = None,
    content_type: Annotated[Optional[str], Header()] = None,
    max_wait_time: Annotated[int, Header(ge=1)] = 300,
    poll_interval: Annotated[int, Header(ge=1)] = 2,
):
    _verify_api_key(authorization)

    try:
        data = await request.body()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lecture body: {e}")

    if not data:
        raise HTTPException(status_code=400, detail="Corps de la requête vide.")

    filename = unquote(x_filename or "document")
    mime_type = content_type or "application/octet-stream"
    logger.info(f"[OpenWebUI] Processing: {filename} ({mime_type}), {len(data)} bytes")

    ctx = RequestContext(user_id=_OPENWEBUI_USER_ID)

    try:
        upload_file_obj = UploadFile(
            filename=filename,
            file=BytesIO(data),
            size=len(data),
            headers=Headers({"content-type": mime_type}),
        )
        task_result = await upload_file(
            file=upload_file_obj,
            group_id="OPENWEBUI",
            interest_zone=None,
            task_operation=TaskOperation.DEFAULT,
            ctx=ctx,
        )
    except Exception as e:
        logger.error(f"[OpenWebUI] Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Echec upload: {e}")

    try:
        task = await _poll_task(task_result.id, ctx, max_wait_time, poll_interval)

        if task.output and task.output.pages:
            docs = _build_pages_content(task, filename, mime_type, len(data))
            logger.info(f"[OpenWebUI] Done: {filename} — {len(docs)} page(s)")
            return JSONResponse(content=docs, status_code=200)

        return JSONResponse(
            content=[
                {
                    "page_content": f"[{filename}] traite, aucun texte extrait.",
                    "metadata": {"filename": filename, "task_id": task.id},
                }
            ],
            status_code=200,
        )
    finally:
        await _cleanup_task(task_result.id, ctx)
