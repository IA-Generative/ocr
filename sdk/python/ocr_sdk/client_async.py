"""Async client for OCR API."""

import asyncio
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Union

import httpx

from ocr_sdk.models import (
    Health,
    PaginatedTasks,
    ProcessResponse,
    TaskModel,
    TaskOperation,
    TaskStats,
    TaskStatus,
)
from ocr_sdk.exceptions import OCRAPIError, OCRAuthenticationError, OCRTimeoutError


class AsyncOCRClient:
    """Async client for OCR API.

    Example (static API key):
        >>> async with AsyncOCRClient("http://localhost:5000") as client:
        ...     # Upload a file for OCR processing
        ...     task = await client.create_job("path/to/file.pdf")
        ...     # Wait for completion
        ...     result = await client.wait_for_task(task.id)

    Example (Keycloak username/password - real user identity, roles/groups/is_admin):
        >>> async with AsyncOCRClient("http://localhost:5000") as client:
        ...     await client.login("user@example.com", "hunter2")
        ...     task = await client.create_job("path/to/file.pdf")
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """Initialize the async OCR client.

        Args:
            base_url: Base URL of the OCR API (e.g., "http://localhost:5000")
            api_key: Optional static API key for authentication (mutually exclusive
                with `login()` - whichever sets the `Authorization` header last wins)
            timeout: Default timeout for requests in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._refresh_token: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    def _ensure_client(self):
        """Ensure client is initialized."""
        if self._client is None:
            raise RuntimeError(
                "Client not initialized. Use 'async with AsyncOCRClient(...) as client:'"
            )

    async def _request(
        self,
        method: str,
        endpoint: str,
        _retry_on_401: bool = True,
        **kwargs,
    ) -> httpx.Response:
        """Make an HTTP request. A 401 is retried once after a silent token refresh
        if a refresh token is available (see `login`/`refresh`) - `_retry_on_401` is
        set to `False` internally on that retry, and by `login`/`_try_refresh`
        themselves, so a failing auth call never loops."""
        self._ensure_client()

        try:
            response = await self._client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response
        except httpx.TimeoutException as e:
            raise OCRTimeoutError(f"Request timed out: {e}")
        except httpx.HTTPStatusError as e:
            if (
                e.response.status_code == 401
                and _retry_on_401
                and await self._try_refresh()
            ):
                return await self._request(
                    method, endpoint, _retry_on_401=False, **kwargs
                )
            raise OCRAPIError(
                status_code=e.response.status_code,
                message=e.response.text,
            )

    def _set_tokens(self, data: dict) -> None:
        self.api_key = data["access_token"]
        self._refresh_token = data.get("refresh_token")
        if self._client is not None:
            self._client.headers["Authorization"] = f"Bearer {self.api_key}"

    async def _try_refresh(self) -> bool:
        """Best-effort refresh, used internally by `_request` on a 401. Returns
        False (never raises) if there is no refresh token or the exchange fails -
        the caller falls back to surfacing the original 401 as `OCRAPIError`."""
        if not self._refresh_token:
            return False
        try:
            response = await self._request(
                "POST",
                "/api/auth/refresh",
                _retry_on_401=False,
                json={"refresh_token": self._refresh_token},
            )
        except OCRAPIError:
            self._refresh_token = None
            return False
        self._set_tokens(response.json())
        return True

    async def login(self, username: str, password: str) -> None:
        """Authenticate with a Keycloak username/password, and use the resulting
        access token for subsequent requests instead of `api_key`.

        Calls this API's own `POST /api/auth/token`, which performs the Keycloak
        exchange server-side (the client secret never leaves the backend, and the
        SDK never talks to Keycloak directly). Requires the Keycloak client to have
        "Direct Access Grants" enabled.

        The access token this returns is short-lived (5 minutes by default in
        Keycloak); a `refresh_token` is also stored, and used automatically to
        get a new access token whenever a request hits a 401 - `refresh()` is
        only needed to renew it ahead of time, e.g. before a long idle period.

        Args:
            username: Keycloak username (or email, depending on realm config)
            password: Keycloak password

        Raises:
            OCRAuthenticationError: If the credentials are rejected
        """
        try:
            response = await self._request(
                "POST",
                "/api/auth/token",
                _retry_on_401=False,
                json={"username": username, "password": password},
            )
        except OCRAPIError as e:
            raise OCRAuthenticationError(f"Login failed: {e.message}")

        self._set_tokens(response.json())

    async def refresh(self) -> None:
        """Exchange the stored refresh token for a new access/refresh token pair.

        Not required for normal use - `_request` already calls this automatically
        the first time a request gets a 401. Useful to renew proactively (e.g.
        before a long idle period) rather than reactively.

        Raises:
            OCRAuthenticationError: If there is no refresh token (call `login()`
                first) or Keycloak rejects it (expired/already used/revoked) -
                call `login()` again in that case.
        """
        if not self._refresh_token:
            raise OCRAuthenticationError(
                "No refresh token available - call login() first"
            )
        if not await self._try_refresh():
            raise OCRAuthenticationError("Token refresh failed - call login() again")

    async def get_health(self) -> Health:
        """Get health status of the API.

        Returns:
            Health object with API status
        """
        response = await self._request("GET", "/api/health")
        return Health(**response.json())

    async def create_job(
        self,
        file_path: Union[str, Path],
        group_id: str = "DEFAULT",
        interest_zone: Optional[str] = None,
        task_operation: TaskOperation = TaskOperation.DEFAULT,
        with_layout: bool = True,
    ) -> TaskModel:
        """Create a new OCR job from a local file.

        Args:
            file_path: Path to the file to process
            group_id: Group ID for the task
            interest_zone: Optional JSON string defining regions of interest
            task_operation: Type of operation to perform
            with_layout: Also detect the layout (tables, images, formulas) of images
                and PDFs; see ``extras["layout_status"]`` for its progress

        Returns:
            TaskModel with job details
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Prepare form data
        with open(file_path, "rb") as f:
            files = {
                "file": (file_path.name, f),
            }

            data = {
                "group_id": group_id,
                "task_operation": task_operation.value,
                "with_layout": str(with_layout).lower(),
            }

            if interest_zone:
                data["interest_zone"] = interest_zone

            response = await self._request(
                "POST",
                "/api/jobs/",
                files=files,
                data=data,
            )

        return TaskModel(**response.json())

    async def get_task(self, task_id: str) -> TaskModel:
        """Get task details by ID.

        Args:
            task_id: Task ID

        Returns:
            TaskModel with task details
        """
        response = await self._request("GET", f"/api/tasks/{task_id}")
        return TaskModel(**response.json())

    async def get_task_page_image(self, task_id: str, page_number: int) -> bytes:
        """Download the rendered image of one page (1-indexed) of a task.

        Args:
            task_id: Task ID
            page_number: 1-indexed page number

        Returns:
            Raw image bytes
        """
        response = await self._request(
            "GET", f"/api/tasks/{task_id}/page/{page_number}"
        )
        return response.content

    async def get_user_tasks(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> PaginatedTasks:
        """Get tasks for the authenticated user.

        Args:
            page: Page number (1-indexed)
            page_size: Number of tasks per page (max 100)

        Returns:
            Paginated list of TaskModel objects (``total``/``page``/``page_size``/``items``)
        """
        response = await self._request(
            "GET",
            "/api/tasks/user/",
            params={"page": page, "page_size": page_size},
        )
        return PaginatedTasks(**response.json())

    async def get_task_stats(self, page: int = 1, page_size: int = 10) -> TaskStats:
        """Get global and per-user task statistics.

        Args:
            page: Page number, forwarded as pagination for the (currently unused)
                admin per-user breakdown
            page_size: Page size, same caveat as ``page``

        Returns:
            TaskStats with ``global_stats`` and ``user_stats``
        """
        response = await self._request(
            "GET",
            "/api/stats/tasks",
            params={"page": page, "page_size": page_size},
        )
        return TaskStats(**response.json())

    async def get_users_count_today(self) -> int:
        """Count distinct users who created a task today.

        Returns:
            Number of distinct users
        """
        response = await self._request("GET", "/api/users/count-users-today")
        return response.json()["users_today"]

    async def delete_task(self, task_id: str) -> None:
        """Delete a task (and its stored result) by ID.

        Args:
            task_id: Task ID
        """
        await self._request("DELETE", f"/api/tasks/{task_id}")

    async def delete_tasks_by_date_and_status(
        self,
        start_date: datetime,
        end_date: datetime,
        status: TaskStatus,
    ) -> None:
        """Bulk-delete tasks in a date range with a given status (admin only).

        Args:
            start_date: Range start (inclusive)
            end_date: Range end (inclusive)
            status: Task status to match
        """
        await self._request(
            "DELETE",
            "/api/v1/tasks/",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "status": status.value,
            },
        )

    async def get_task_text(self, task_id: str) -> str:
        """Get extracted text from a completed task.

        Args:
            task_id: Task ID

        Returns:
            Extracted text content
        """
        response = await self._request("GET", f"/api/text-task/{task_id}")
        return response.text

    async def get_task_value(
        self,
        task_id: str,
        transform: str = "text",
    ) -> Union[str, bytes, List[Any], dict]:
        """Get a task's output in one of several transformed shapes.

        Args:
            task_id: Task ID
            transform: One of ``"text"`` (plain extracted text, default),
                ``"form"`` (list of per-page form entries), ``"form-csv"``
                (form entries as CSV bytes), or ``"only-result"`` (raw OCR
                result JSON as a dict)

        Returns:
            ``str`` for ``"text"``, ``list`` for ``"form"``, ``bytes`` for
            ``"form-csv"``, ``dict`` for ``"only-result"``
        """
        response = await self._request(
            "GET",
            f"/api/task-to-value/{task_id}",
            params={"transform": transform},
        )
        if transform == "form-csv":
            return response.content
        if transform in ("text",):
            return response.text
        return response.json()

    async def process_document(
        self,
        file_path: Union[str, Path],
        mime_type: Optional[str] = None,
        max_wait_time: int = 300,
        poll_interval: int = 2,
    ) -> List[ProcessResponse]:
        """Upload a document and block until OCR completes (or times out).

        This is the OpenWebUI-style convenience endpoint (``PUT /process``): a single
        call that uploads, polls, and returns per-page content - as opposed to
        ``create_job`` + ``wait_for_task``, which give you the intermediate
        ``TaskModel`` at each step.

        Args:
            file_path: Path to the file to process
            mime_type: Content type of the file; guessed from the extension if unset
            max_wait_time: Max seconds the server should wait for completion
            poll_interval: Seconds between the server's internal status checks

        Returns:
            List of ``ProcessResponse`` (one per page)
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content_type = (
            mime_type
            or mimetypes.guess_type(file_path.name)[0]
            or "application/octet-stream"
        )

        response = await self._request(
            "PUT",
            "/api/process",
            content=file_path.read_bytes(),
            headers={
                "max_wait_time": str(max_wait_time),
                "poll_interval": str(poll_interval),
                "X-Filename": file_path.name,
                "Content-Type": content_type,
            },
            timeout=max(self.timeout, max_wait_time + 10),
        )
        return [ProcessResponse(**item) for item in response.json()]

    async def wait_for_task(
        self,
        task_id: str,
        poll_interval: float = 2.0,
        max_wait_time: float = 300.0,
    ) -> TaskModel:
        """Wait for a task to complete.

        Args:
            task_id: Task ID
            poll_interval: Time between status checks in seconds
            max_wait_time: Maximum time to wait in seconds

        Returns:
            Completed TaskModel

        Raises:
            OCRTimeoutError: If task doesn't complete within max_wait_time
            OCRAPIError: If task fails
        """
        elapsed = 0.0

        while elapsed < max_wait_time:
            task = await self.get_task(task_id)

            if task.status == TaskStatus.COMPLETED.value:
                return task
            elif task.status == TaskStatus.FAILED.value:
                error = (
                    task.extras.get("error", "Unknown error")
                    if task.extras
                    else "Unknown error"
                )
                raise OCRAPIError(500, f"Task failed: {error}")

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise OCRTimeoutError(
            f"Task {task_id} did not complete within {max_wait_time}s"
        )
