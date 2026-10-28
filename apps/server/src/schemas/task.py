import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict
from sqlalchemy import FLOAT, JSON, BigInteger, Column, Integer, String, func

from src.connector.db_connector import Base, get_db
from src.logger import logger
from src.schemas.audio import AudioTranscriptionResult
from src.schemas.input import InputForm
from src.schemas.output import OCRResult
from src.schemas.video import VideoDescriptionResult

TaskOutput = Union[OCRResult, AudioTranscriptionResult, VideoDescriptionResult]


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False, primary_key=True)
    status = Column(String, default="queued")
    user_id = Column(String, nullable=False)
    group_id = Column(String, nullable=True)
    percentage = Column(FLOAT, nullable=False)
    input = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    position = Column(Integer, nullable=True)
    created_at = Column(BigInteger, default=lambda: int(datetime.now().timestamp()))
    updated_at = Column(
        BigInteger,
        default=lambda: int(datetime.now().timestamp()),
        onupdate=lambda: int(datetime.now().timestamp()),
    )
    parameters = Column(JSON, nullable=True)

    extras = Column(JSON, nullable=True)
    content_hash = Column(String, nullable=True, index=True, unique=False)


class TaskModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    group_id: Optional[str] = None
    type: str
    status: str = "queued"
    percentage: Optional[float] = 0.0
    input: Optional[InputForm] = None
    output: Optional[TaskOutput] = None
    created_at: int
    updated_at: int
    extras: Optional[Dict[str, Any]] = None
    position: Optional[int] = None
    content_hash: Optional[str] = None


class TaskForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    group_id: Optional[str] = None
    type: Optional[str] = None
    status: str
    percentage: Optional[float] = 0.0
    extras: Optional[dict] = None
    input: Optional[InputForm] = None
    output: Optional[TaskOutput] = None
    content_hash: Optional[str] = None


class TaskUpdateForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    group_id: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    percentage: Optional[float] = 0.0
    extras: Optional[dict] = None
    input: Optional[InputForm] = None
    output: Optional[TaskOutput] = None
    content_hash: Optional[str] = None


class TaskStatus(str, Enum):
    CREATED = "created"  # Tâche instanciée mais pas encore mise en file
    QUEUED = "queued"  # En attente dans une file de traitement
    STARTED = "started"  # A commencé à être traitée
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"  # Traitée avec succès
    FAILED = "failed"  # Erreur fatale
    RETRYING = "retrying"  # En cours de nouvelle tentative après échec
    CANCELED = "canceled"  # Annulée manuellement ou par logique métier
    TIMEOUT = "timeout"  # N’a pas pu terminer dans le temps imparti


class TaskOperation(str, Enum):
    OCR: str = "ocr"
    DEFAULT: str = "default"
    SAVE_TEMPLATE: str = "save_template"
    FORMS: str = "forms"
    VECTORIZE: str = "vectorize"
    DOCLING: str = "docling"


class TaskStatsGlobal(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    total_tasks: int
    # Clé = status, Valeur = nombre de tâches
    tasks_stats: Dict[TaskStatus, int]


class TaskStatsUser(TaskStatsGlobal):
    model_config = ConfigDict(from_attributes=True)
    user_id: str


class TaskStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    global_stats: TaskStatsGlobal
    user_stats: TaskStatsUser
    # all_users_stats: Pagination[TaskStatsUser] = Field(
    #     None, description="Statistiques paginées pour tous les utilisateurs"
    # )


class TaskTable:
    def __init__(self, get_db):
        self.get_db = get_db

    def insert_new_task(self, user_id: str, form_data: TaskForm) -> Optional[TaskModel]:
        with self.get_db() as db:
            knowledge = TaskModel(
                **{
                    **form_data.model_dump(),
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )

            result = Task(**knowledge.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            return TaskModel.model_validate(result)

    def get_task_by_id(self, task_id: str) -> Optional[TaskModel]:
        with self.get_db() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                logger.warning(f"Task with id {task_id} not found.")
                return None
            return TaskModel.model_validate(task)

    def get_tasks_by_id(self, task_id: str) -> Optional[list[TaskModel]]:
        with self.get_db() as db:
            tasks = db.query(Task).filter(Task.id == task_id).all()
            if not tasks:
                logger.warning(f"Task with id {task_id} not found.")
                return None
            return [TaskModel.model_validate(task) for task in tasks]

    def get_task_by_pks(self, task_id: str, task_type: str) -> Optional[TaskModel]:
        with self.get_db() as db:
            task = db.query(Task).filter(Task.id == task_id, Task.type == task_type).first()
            if not task:
                logger.warning(f"Task with id {task_id} not found.")
                return None
            return TaskModel.model_validate(task)

    def update_task(self, task_id: str, form_data: TaskUpdateForm) -> Optional[TaskModel]:
        with self.get_db() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                logger.warning(f"Task with id {task_id} not found.")
                return None

            updates = form_data.model_dump(exclude_unset=True)

            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)

            if form_data.input:
                task.input = form_data.input.model_dump()

            if form_data.output:
                task.output = form_data.output.model_dump()

            task.updated_at = int(time.time())
            db.commit()
            db.refresh(task)
            return TaskModel.model_validate(task)

    def delete_task_by_id(self, task_id: str) -> Optional[TaskModel]:
        with self.get_db() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                logger.warning(f"Task with id {task_id} not found.")
                return None
            db.delete(task)
            db.commit()
            return TaskModel.model_validate(task)

    def get_tasks_by_user_id(self, user_id: str, page: int = 1, page_size: int = 10) -> Optional[List[TaskModel]]:
        offset = (page - 1) * page_size
        with self.get_db() as db:
            # Without an explicit order OFFSET/LIMIT pages overlap and skip rows; newest first
            # matches what the task list shows, `id` makes equal timestamps deterministic.
            tasks = (
                db.query(Task)
                .filter(Task.user_id == user_id)
                .order_by(Task.created_at.desc(), Task.id)
                .offset(offset)
                .limit(page_size)
                .all()
            )

            if not tasks:
                logger.warning(f"No tasks found for user {user_id}.")
                return None

            return [TaskModel.model_validate(task) for task in tasks]

    def count_tasks_by_user_id(self, user_id: str) -> int:
        with self.get_db() as db:
            count = db.query(func.count(Task.id)).filter(Task.user_id == user_id).scalar()
            return count

    def delete_tasks_by_user_id(self, user_id: str) -> Optional[List[TaskModel]]:
        with self.get_db() as db:
            tasks_to_delete = db.query(Task).filter(Task.user_id == user_id).all()

            if not tasks_to_delete:
                logger.warning(f"No tasks found for user {user_id}.")
                return None

            for task in tasks_to_delete:
                db.delete(task)
            db.commit()

            return [TaskModel.model_validate(task) for task in tasks_to_delete]

    def get_position_in_queue(self, task_id: str) -> int | None:
        if task_id:
            with self.get_db() as db:
                task = db.query(Task).filter(Task.id == task_id).first()
                if not task:
                    return None

                if task.status != TaskStatus.QUEUED:
                    return None

                position = (
                    db.query(func.count(Task.id))  # noqa
                    .filter(
                        Task.status == TaskStatus.QUEUED,
                        Task.created_at < task.created_at,
                    )
                    .scalar()
                )

                return position

    def get_task_by_content_hash(self, content_hash_value: str) -> Optional[TaskModel]:
        with self.get_db() as db:
            task = db.query(Task).filter(Task.content_hash == content_hash_value).first()
            return TaskModel.model_validate(task) if task else None

    def delete_tasks_by_date_and_status(
        self, start_date: datetime, end_date: datetime, status: TaskStatus
    ) -> Optional[List[TaskModel]]:
        with self.get_db() as db:
            tasks_to_delete = (
                db.query(Task)
                .filter(
                    Task.created_at >= int(start_date.timestamp()),
                    Task.created_at <= int(end_date.timestamp()),
                    Task.status == status.value,
                )
                .all()
            )

            if not tasks_to_delete:
                logger.warning(f"No tasks found between {start_date} and {end_date}.")
                return None

            for task in tasks_to_delete:
                db.delete(task)
            db.commit()

            return [TaskModel.model_validate(task) for task in tasks_to_delete]

    def delete_tasks_created_before(
        self,
        cutoff_date: datetime,
        statuses: Optional[List[TaskStatus]] = None,
        batch_size: int = 100,
    ) -> List[TaskModel]:
        """Delete every task created before `cutoff_date`, in batches of `batch_size`.

        Used by the periodic purge task (see `ocr_backend/purge.py`). Restricting to
        `statuses` avoids deleting tasks that are still queued/in-progress: without a
        filter, a slow task older than the retention window would be purged mid-run.
        No offset/pagination is needed between batches: each deleted row stops
        matching `Task.created_at < cutoff_ts`, so the same query naturally yields
        the next batch.
        """
        cutoff_ts = int(cutoff_date.timestamp())
        deleted: List[TaskModel] = []
        with self.get_db() as db:
            query = db.query(Task).filter(Task.created_at < cutoff_ts)
            if statuses:
                query = query.filter(Task.status.in_([s.value for s in statuses]))

            while True:
                batch = query.limit(batch_size).all()
                if not batch:
                    break
                deleted.extend(TaskModel.model_validate(task) for task in batch)
                for task in batch:
                    db.delete(task)
                db.commit()

        return deleted

    def get_tasks_by_group_id(self, group_id: str, page: int = 1, page_size: int = 10) -> Optional[List[TaskModel]]:
        offset = (page - 1) * page_size
        with self.get_db() as db:
            tasks = (
                db.query(Task)
                .filter(Task.group_id == group_id)
                .order_by(Task.created_at.desc(), Task.id)
                .offset(offset)
                .limit(page_size)
                .all()
            )

            if not tasks:
                logger.warning(f"No tasks found for group {group_id}.")
                return None

            return [TaskModel.model_validate(task) for task in tasks]

    def delete_tasks_by_group_id(self, group_id: str) -> Optional[List[TaskModel]]:
        with self.get_db() as db:
            tasks_to_delete = db.query(Task).filter(Task.group_id == group_id).all()

            if not tasks_to_delete:
                logger.warning(f"No tasks found for group {group_id}.")
                return None

            for task in tasks_to_delete:
                db.delete(task)
            db.commit()

            return [TaskModel.model_validate(task) for task in tasks_to_delete]

    def statistics(self, user_id: str, is_admin: bool = False, skip: int = 0, limit: int = 10) -> TaskStats:
        with get_db() as db:
            # statistiques User

            # Statistiques globales
            total_tasks = db.query(func.count(Task.id)).scalar()

            tasks_stats = (
                db.query(Task.status, func.count(Task.id))  # noqa
                .group_by(Task.status)
                .all()
            )
            tasks_stats_dict = {status: count for status, count in tasks_stats}

            global_stats = TaskStatsGlobal(total_tasks=total_tasks, tasks_stats=tasks_stats_dict)

            # Statistiques de l'utilisateur courant
            user_total_tasks = db.query(func.count(Task.id)).filter(Task.user_id == user_id).scalar()
            user_tasks_stats = (
                db.query(Task.status, func.count(Task.id))  # noqa
                .filter(Task.user_id == user_id)
                .group_by(Task.status)
                .all()
            )
            user_tasks_stats_dict = {status: count for status, count in user_tasks_stats}
            user_stats = TaskStatsUser(user_id=user_id, total_tasks=user_total_tasks, tasks_stats=user_tasks_stats_dict)

            # # Statistiques par utilisateur (paginated)
            # user_stats_list = []
            # pagination_stats = None
            # if is_admin:
            #     user_stats_count = db.query(func.count(
            #         func.distinct(Task.user_id))).scalar()
            #     user_stats_query = (
            #         db.query(Task.user_id, func.count(Task.id))  # noqa
            #         .group_by(Task.user_id)
            #         .offset(skip)
            #         .limit(limit)
            #         .all()
            #     )

            #     for user_id, count in user_stats_query:
            #         user_tasks_stats = (
            #             db.query(Task.status, func.count(Task.id))  # noqa
            #             .filter(Task.user_id == user_id)
            #             .group_by(Task.status)
            #             .all()
            #         )
            #         user_tasks_stats_dict = {
            #             status: count for status, count in user_tasks_stats}
            #         user_stats_list.append(
            #             TaskStatsUser(user_id=user_id, total_tasks=count,
            #                           tasks_stats=user_tasks_stats_dict)
            #         )
            #     pagination_stats = Pagination[TaskStatsUser](
            #         total=user_stats_count, page=skip // limit + 1, page_size=limit, items=user_stats_list
            #     )

            return TaskStats(global_stats=global_stats, all_users_stats=None, user_stats=user_stats)

    def count_unique_users_between_dates(self, start_date: int, end_date: int) -> int:
        with get_db() as db:
            unique_users = (
                db.query(Task.user_id)
                .filter(Task.created_at >= start_date, Task.created_at <= end_date)
                .distinct()
                .count()
            )
            return unique_users


task_table = TaskTable(get_db)
