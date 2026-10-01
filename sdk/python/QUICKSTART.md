# Quick Start Guide

## Installation

### Using uv (Recommended)

#### From Git Repository

**Option 1: SSH** (requires SSH keys configured)

```bash
uv add git@github.com:IA-Generative/ocr.git#subdirectory=sdk/python
```

**Option 2: HTTPS with GitHub Token** (for private repos)

```bash
# First, set your GitHub token
export GITHUB_TOKEN=your_personal_access_token

# Then install
uv add https://${GITHUB_TOKEN}@github.com/IA-Generative/ocr.git#subdirectory=sdk/python
```

**Option 3: GitHub CLI** (if `gh` is installed and authenticated)

```bash
uv add https://github.com/IA-Generative/ocr.git#subdirectory=sdk/python
```

#### From Local Directory

```bash
# Navigate to the SDK directory
cd sdk

# Install the SDK in your project
uv pip install -e .
```

### Using pip

#### From Git Repository (subdirectory)

`sdk/` lives inside this monorepo rather than its own repository, so `pip` needs the
`#subdirectory=` fragment to find `sdk/pyproject.toml`:

```bash
pip install "git+https://github.com/IA-Generative/ocr.git#subdirectory=sdk"
```

#### From Local Directory

```bash
cd sdk
pip install -e .
```

## Basic Usage

### Sync Client (Simple)

```python
from ocr_sdk import SyncOCRClient

# Create client
with SyncOCRClient("http://localhost:5000") as client:
    # Check health
    health = client.get_health()
    print(f"API is {health.status}")

    # Process a document
    task = client.create_job("document.pdf")
    result = client.wait_for_task(task.id)

    # Get text
    text = client.get_task_text(task.id)
    print(text)
```

### Async Client (Advanced)

```python
import asyncio
from ocr_sdk import AsyncOCRClient

async def process_document():
    async with AsyncOCRClient("http://localhost:5000") as client:
        # Create and wait for job
        task = await client.create_job("document.pdf")
        result = await client.wait_for_task(task.id)

        # Get text
        text = await client.get_task_text(task.id)
        print(text)

asyncio.run(process_document())
```

### Authenticating as a Keycloak User (username/password)

For a static API key, pass `api_key=...` to the constructor. To authenticate as a real
Keycloak identity instead (so requests carry your actual roles/groups), call `login()`
after entering the context manager - it exchanges your credentials for an access token
via this API's own `POST /api/auth/token` (the Keycloak client secret never leaves the
backend):

```python
with SyncOCRClient("http://localhost:5000") as client:
    client.login("user@example.com", "hunter2")
    task = client.create_job("document.pdf")
```

The access token expires (5 minutes by default in Keycloak), but a refresh token is
stored too and used automatically to renew it whenever a request hits a 401 - no need
to call `login()` again yourself. Call `client.refresh()` to renew proactively, or
catch `OCRAuthenticationError` and call `login()` again if the refresh token itself has
expired.

## Import in Your Project

Once installed, you can import the SDK in any Python file:

```python
# Basic imports
from ocr_sdk import SyncOCRClient, AsyncOCRClient

# Models
from ocr_sdk import TaskModel, TaskStatus, TaskOperation, Health

# Exceptions
from ocr_sdk.exceptions import OCRAPIError, OCRTimeoutError
```

## Examples

Check the `examples/` directory for complete usage examples:
- `sync_example.py` - Comprehensive synchronous client example
- `async_example.py` - Comprehensive asynchronous client example with concurrent processing

## API Reference

### SyncOCRClient / AsyncOCRClient

Both clients have the same methods (async methods use `await`):

- `login(username, password)` - Authenticate as a Keycloak user (see above)
- `refresh()` - Proactively renew the access token (called automatically on a 401)
- `get_health()` - Get API health status
- `create_job(file_path, ...)` - Upload file and create OCR job
- `get_task(task_id)` - Get task details
- `get_task_page_image(task_id, page_number)` - Download a page's rendered image
- `get_user_tasks(page, page_size)` - List user's tasks (paginated - `.items`/`.total`)
- `get_task_stats(...)` - Global and per-user task statistics
- `get_users_count_today()` - Count distinct users active today
- `delete_task(task_id)` - Delete a task
- `delete_tasks_by_date_and_status(...)` - Bulk-delete tasks (admin only)
- `get_task_text(task_id)` - Get extracted text
- `get_task_value(task_id, transform=...)` - Get task output as text/form/CSV/raw JSON
- `wait_for_task(task_id, ...)` - Wait for task completion
- `process_document(file_path, ...)` - One-step upload and wait

> `template`/`collections` API routes exist in the backend codebase but aren't
> currently mounted on the running app (see `ocr_backend/main.py`) - no SDK methods
> call them, since they'd 404.

### Configuration

```python
client = SyncOCRClient(
    base_url="http://localhost:5000",  # API URL
    api_key="your-token",               # Optional auth token
    timeout=30.0                        # Request timeout in seconds
)
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check the [examples/](examples/) directory for complete code examples
- Review the [models.py](ocr_sdk/models.py) to understand all available data structures
