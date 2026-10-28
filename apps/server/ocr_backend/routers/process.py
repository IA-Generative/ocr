from fastapi import APIRouter, Header, HTTPException, Request, Depends, UploadFile
from fastapi.responses import JSONResponse
from typing import Optional
from io import BytesIO
import asyncio

from ocr_backend.routers.jobs import upload_file
from ocr_backend.routers.task import get_task_by_id_user
from ocr_backend.core.security.token import RequestContext
from ocr_backend.core.security.factory import TokenVerifier
from src.schemas.task import TaskOperation, TaskStatus, TaskModel
from src.logger import logger

process_router = APIRouter(tags=["Process"])


# TODO: Refactor to avoid code duplication with jobs.py
def get_pages_content(task: TaskModel, size_bytes: int, filename: str, mime_type: str) -> list:
    response = []
    for page in task.output.pages:
        page_content = task.output.set_page_text(page)
        response.append(
            {
                "page_content": page_content,
                "metadata": {
                    "filename": filename,
                    "mime_type": mime_type,
                    "size_bytes": size_bytes,
                    "task_id": task.id,
                },
            }
        )
    return response


@process_router.put(
    "/process",
    summary="Upload a document and wait for its result",
    description=(
        "One-shot alternative to `POST /jobs/` + polling `GET /tasks/{task_id}`: "
        "uploads the raw request body as a file, then blocks (up to `max_wait_time` "
        "seconds, checking every `poll_interval` seconds) until the job completes, "
        "returning the extracted per-page content directly.\n\n"
        "The file itself is the request body (not multipart) - set `X-Filename` and "
        "`Content-Type` to describe it, e.g. from `curl --data-binary @file.pdf`."
    ),
    responses={
        400: {"description": "Empty request body"},
        408: {"description": "Job didn't complete within `max_wait_time`"},
        500: {"description": "Job processing failed"},
    },
)
async def process_document(
    request: Request,
    max_wait_time: int = Header(300, ge=1),
    poll_interval: int = Header(2, ge=1),
    x_filename: Optional[str] = Header(None),
    content_type: Optional[str] = Header(None),
    ctx: RequestContext = Depends(TokenVerifier),
):
    try:
        data = await request.body()
        if not data:
            raise HTTPException(status_code=400, detail="Empty file data")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading body: {e}")

    filename = x_filename or "unknown_file"
    mime_type = content_type or "application/octet-stream"

    logger.info(f"Processing file: {filename} ({mime_type}), size={len(data)} bytes")

    try:
        # Créer un UploadFile à partir des données reçues
        file_like = BytesIO(data)
        upload_file_obj = UploadFile(
            filename=filename,
            file=file_like,
            size=len(data),
            headers={"content-type": mime_type},
        )

        task_result = await upload_file(
            file=upload_file_obj,
            group_id="OWUI_EXTERNAL",
            interest_zone=None,
            task_operation=TaskOperation.DEFAULT,
            ctx=ctx,
        )

        logger.info(f"Task created with ID: {task_result.id}")

        elapsed_time = 0

        while elapsed_time < max_wait_time:
            task = await get_task_by_id_user(task_result.id, ctx=ctx)

            if task.status == TaskStatus.COMPLETED.value:
                # Tâche terminée avec succès
                if task.output and task.output.pages:
                    # Construire la réponse avec les résultats OCR
                    response = get_pages_content(
                        task,
                        size_bytes=len(data),
                        filename=filename,
                        mime_type=mime_type,
                    )

                    return JSONResponse(content=response, status_code=200)
                else:
                    response = [
                        {
                            "page_content": f"Le fichier {filename} a été traité mais aucun texte n'a été extrait.",
                            "metadata": {
                                "filename": filename,
                                "mime_type": mime_type,
                                "size_bytes": len(data),
                                "task_id": task_result.id,
                            },
                        }
                    ]
                    return JSONResponse(content=response, status_code=200)

            elif task.status == TaskStatus.FAILED.value:
                # Tâche échouée
                error_detail = task.extras.get("error", "Unknown error") if task.extras else "Unknown error"
                raise HTTPException(status_code=500, detail=f"OCR processing failed: {error_detail}")

            # Attendre avant la prochaine vérification
            await asyncio.sleep(poll_interval)
            elapsed_time += poll_interval

        # Timeout atteint
        raise HTTPException(status_code=408, detail=f"Processing timeout. Task ID: {task_result.id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
