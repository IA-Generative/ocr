import json
from json import JSONDecodeError
import os
import aiofiles
import traceback
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, status, Depends, Form
import pymupdf

from src.connector.broker_connector import celery_app, celery_config
from src.logger import logger
from src.schemas.input import InputForm, RegionOfInterest
from src.schemas.task import (
    TaskForm,
    TaskModel,
    TaskOperation,
    TaskStatus,
    TaskUpdateForm,
    task_table,
)
from ocr_backend.core.security.token import RequestContext
from ocr_backend.core.security.factory import TokenVerifier

from ..connectors import s3_client_connector

router = APIRouter(tags=["Jobs"])
WORKER_NAME = "worker.tasks.ocr"


def _handle_pdf_interest_zone(file_path: str, interest_zone: Optional[str]) -> list[RegionOfInterest]:
    doc = pymupdf.open(file_path)
    if doc.is_form_pdf:
        return []
    try:
        regions = [RegionOfInterest(**item) for item in json.loads(interest_zone)]
        if len(regions) != len(doc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Interest zone cannot be empty for PDF files {traceback.format_exc()}",
            )
        return regions
    except JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format for interest_zone {e}{traceback.format_exc()}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format for interest_zone {e}{traceback.format_exc()}",
        )


def _handle_image_interest_zone(interest_zone: Optional[str]) -> list[RegionOfInterest]:
    regions = [RegionOfInterest(**item) for item in json.loads(interest_zone)]
    if len(regions) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interest zone cannot be empty for image files {traceback.format_exc()}",
        )
    return regions


def verify_interest_zone(
    file_path: str,
    content_type: str,
    interest_zone: Optional[str] = "",
) -> list[RegionOfInterest]:
    if content_type == "application/pdf":
        return _handle_pdf_interest_zone(file_path, interest_zone)
    elif content_type.startswith("image/"):
        return _handle_image_interest_zone(interest_zone)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid content type {traceback.format_exc()}",
        )


@router.post(
    "/jobs/",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskModel,
    summary="Upload a file for OCR/extraction",
    description=(
        "Uploads a file (PDF or image) and queues it for processing. Returns "
        "immediately with the created task in `queued` status - poll `GET "
        "/tasks/{task_id}` or use `PUT /process` for a blocking one-shot call."
    ),
    responses={400: {"description": "Invalid or missing `interest_zone` for the file's content type"}},
)
async def upload_file(
    file: UploadFile = File(...),
    group_id: str = Form("DEFAULT"),
    interest_zone: Optional[str] = Form(None),
    task_operation: TaskOperation = Form(TaskOperation.DEFAULT.value),
    ctx: RequestContext = Depends(TokenVerifier),
):
    extras = {}
    task_data = task_table.insert_new_task(
        user_id=ctx.user_id,
        form_data=TaskForm(
            user_id=ctx.user_id,
            type=task_operation,
            status=TaskStatus.CREATED.value,
            percentage=0.0,
            extras=extras,
            group_id=group_id,
        ),
    )
    try:
        async with aiofiles.tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

            # Lecture par chunks pour économiser la mémoire
            chunk_size = 8192  # 8KB chunks
            while chunk := await file.read(chunk_size):
                await temp_file.write(chunk)
        if interest_zone is not None:
            interest_zone = verify_interest_zone(
                file_path=temp_file_path,
                content_type=file.content_type,
                interest_zone=interest_zone,
            )
    except Exception as e:
        logger.error(f"HTTPException for user {ctx.user_id}, task {task_data.id}: {e} - {traceback.format_exc()}")
        task_table.update_task(
            task_id=task_data.id,
            form_data=TaskUpdateForm(
                type=task_operation,
                status=TaskStatus.FAILED.value,
                extras={"error": str(e)},
            ),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format for interest_zone {e}{traceback.format_exc()}",
        )

    try:
        saved_path = s3_client_connector.save(ctx.user_id, task_data.id, temp_file_path, file.filename)
        logger.debug(f"Save into S3 - {saved_path}")

        _, extension = os.path.splitext(file.filename)

        extras = task_data.extras
        input_form = InputForm(
            storage_file_path=saved_path,
            raw_filename=os.path.basename(file.filename),
            content_type=file.content_type,
            ext=extension,
            size=file.size,
            interest_zone=interest_zone,
        )

        task_data = task_table.update_task(
            task_id=task_data.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.QUEUED.value,
                input=input_form,
                extras=extras,
            ),
        )

        task_data.position = task_table.get_position_in_queue(task_id=task_data.id)
        os.remove(temp_file_path)

        logger.debug(f"{task_data.id} worker name {WORKER_NAME} - {celery_config.CELERY_APP_NAME}" + "\n" + 79 * "*")

        celery_app.send_task(WORKER_NAME, args=[json.dumps(task_data.model_dump())], task_id=task_data.id)

        return task_data

    except Exception as e:
        logger.error(
            f"Failed to upload file for user {ctx.user_id}, task {task_data.id}: {e} - {traceback.format_exc()}"
        )
        task_table.update_task(
            task_id=task_data.id,
            form_data=TaskUpdateForm(
                type=task_operation,
                status=TaskStatus.FAILED.value,
                extras={"error": str(e)},
            ),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {e} {traceback.format_exc()}",
        )
