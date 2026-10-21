import type {
  Health,
  PaginatedTasks,
  ProcessResponse,
  TaskModel,
  TaskOperation,
  TaskStats,
  TaskStatus,
  TaskValueTransform,
} from './types.js'
import { readFile } from 'node:fs/promises'

import { basename, extname } from 'node:path'
import { OCRAPIError, OCRAuthenticationError, OCRTimeoutError } from './errors.js'

export interface OCRClientOptions {
  /**
   * Static API key sent as `Authorization: Bearer <apiKey>`. Mutually exclusive with
   * `login()` - whichever sets the header last wins.
   */
  apiKey?: string
  /** Request timeout in milliseconds. Default: 30000. */
  timeoutMs?: number
}

export interface CreateJobOptions {
  groupId?: string
  interestZone?: string
  taskOperation?: TaskOperation
  /** Also detect the layout (tables, images, formulas) of images and PDFs. Default: true. */
  withLayout?: boolean
}

export interface ProcessDocumentOptions {
  mimeType?: string
  maxWaitTimeSeconds?: number
  pollIntervalSeconds?: number
}

export interface WaitForTaskOptions {
  pollIntervalMs?: number
  maxWaitTimeMs?: number
}

const DEFAULT_TIMEOUT_MS = 30_000
const DEFAULT_GROUP_ID = 'DEFAULT'
const DEFAULT_TASK_OPERATION: TaskOperation = 'default'

const MIME_TYPES: Record<string, string> = {
  '.pdf': 'application/pdf',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.tif': 'image/tiff',
  '.tiff': 'image/tiff',
}

function guessMimeType (filePath: string): string {
  return MIME_TYPES[extname(filePath).toLowerCase()] ?? 'application/octet-stream'
}

/**
 * Client for the MIrAI OCR API (Node.js, `fetch`-based).
 *
 * @example Static API key
 * ```ts
 * const client = new OCRClient('http://localhost:5000', { apiKey: 'your-api-key' })
 * const task = await client.createJob('path/to/file.pdf')
 * const result = await client.waitForTask(task.id)
 * ```
 *
 * @example Keycloak username/password
 * ```ts
 * const client = new OCRClient('http://localhost:5000')
 * await client.login('user@example.com', 'hunter2')
 * const task = await client.createJob('path/to/file.pdf')
 * ```
 */
export class OCRClient {
  private readonly baseUrl: string
  private readonly timeoutMs: number
  private apiKey?: string
  private refreshToken?: string

  constructor (baseUrl: string, options: OCRClientOptions = {}) {
    this.baseUrl = baseUrl.replace(/\/+$/, '')
    this.timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS
    this.apiKey = options.apiKey
  }

  /**
   * A 401 is retried once after a silent token refresh if a refresh token is
   * available (see `login`/`refresh`) - `retryOn401: false` is passed internally on
   * that retry, and by `login`/`tryRefresh` themselves, so a failing auth call never
   * loops.
   */
  private async request (
    path: string,
    init: RequestInit = {},
    { timeoutMs = this.timeoutMs, retryOn401 = true }: { timeoutMs?: number, retryOn401?: boolean } = {},
  ): Promise<Response> {
    const headers = new Headers(init.headers)
    if (this.apiKey) {
      headers.set('Authorization', `Bearer ${this.apiKey}`)
    }

    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), timeoutMs)

    let response: Response
    try {
      response = await fetch(`${this.baseUrl}${path}`, { ...init, headers, signal: controller.signal })
    }
    catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        throw new OCRTimeoutError(`Request timed out after ${timeoutMs}ms: ${path}`)
      }
      throw err
    }
    finally {
      clearTimeout(timer)
    }

    if (!response.ok) {
      if (response.status === 401 && retryOn401 && await this.tryRefresh()) {
        return this.request(path, init, { timeoutMs, retryOn401: false })
      }
      const body = await response.text().catch(() => '')
      throw new OCRAPIError(response.status, body)
    }
    return response
  }

  private setTokens (data: { access_token: string, refresh_token?: string }): void {
    this.apiKey = data.access_token
    this.refreshToken = data.refresh_token
  }

  /**
   * Best-effort refresh, used internally by `request` on a 401. Returns `false`
   * (never throws) if there is no refresh token or the exchange fails - the caller
   * falls back to surfacing the original 401 as `OCRAPIError`.
   */
  private async tryRefresh (): Promise<boolean> {
    if (!this.refreshToken) {
      return false
    }
    let response: Response
    try {
      response = await this.request(
        '/api/auth/refresh',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: this.refreshToken }),
        },
        { retryOn401: false },
      )
    }
    catch {
      this.refreshToken = undefined
      return false
    }
    this.setTokens((await response.json()) as { access_token: string, refresh_token: string })
    return true
  }

  /**
   * Authenticate with a Keycloak username/password, and use the resulting access
   * token for subsequent requests instead of a static API key.
   *
   * Calls this API's own `POST /api/auth/token`, which performs the Keycloak exchange
   * server-side (the client secret never leaves the backend, and the SDK never talks
   * to Keycloak directly). Requires the Keycloak client to have "Direct Access Grants"
   * enabled.
   *
   * The access token this returns is short-lived (5 minutes by default in Keycloak);
   * a refresh token is also stored, and used automatically to get a new access token
   * whenever a request hits a 401 - `refresh()` is only needed to renew it ahead of
   * time, e.g. before a long idle period.
   */
  async login (username: string, password: string): Promise<void> {
    let response: Response
    try {
      response = await this.request(
        '/api/auth/token',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        },
        { retryOn401: false },
      )
    }
    catch (err) {
      if (err instanceof OCRAPIError) {
        throw new OCRAuthenticationError(`Login failed: ${err.body}`)
      }
      throw err
    }

    this.setTokens((await response.json()) as { access_token: string, refresh_token: string })
  }

  /**
   * Exchange the stored refresh token for a new access/refresh token pair.
   *
   * Not required for normal use - `request` already calls this automatically the
   * first time a request gets a 401. Useful to renew proactively (e.g. before a long
   * idle period) rather than reactively.
   *
   * @throws {OCRAuthenticationError} If there is no refresh token (call `login()`
   * first) or Keycloak rejects it (expired/already used/revoked) - call `login()`
   * again in that case.
   */
  async refresh (): Promise<void> {
    if (!this.refreshToken) {
      throw new OCRAuthenticationError('No refresh token available - call login() first')
    }
    if (!await this.tryRefresh()) {
      throw new OCRAuthenticationError('Token refresh failed - call login() again')
    }
  }

  /** Get health status of the API. */
  async getHealth (): Promise<Health> {
    const response = await this.request('/api/health', { method: 'GET' })
    return (await response.json()) as Health
  }

  /** Upload a local file and queue it for OCR/extraction. */
  async createJob (filePath: string, options: CreateJobOptions = {}): Promise<TaskModel> {
    const data = await readFile(filePath)
    const form = new FormData()
    form.append('file', new Blob([new Uint8Array(data)], { type: guessMimeType(filePath) }), basename(filePath))
    form.append('group_id', options.groupId ?? DEFAULT_GROUP_ID)
    form.append('task_operation', options.taskOperation ?? DEFAULT_TASK_OPERATION)
    form.append('with_layout', String(options.withLayout ?? true))
    if (options.interestZone) {
      form.append('interest_zone', options.interestZone)
    }

    const response = await this.request('/api/jobs/', { method: 'POST', body: form })
    return (await response.json()) as TaskModel
  }

  /** Get task details by ID. */
  async getTask (taskId: string): Promise<TaskModel> {
    const response = await this.request(`/api/tasks/${encodeURIComponent(taskId)}`, { method: 'GET' })
    return (await response.json()) as TaskModel
  }

  /** Download the rendered image of one page (1-indexed) of a task. */
  async getTaskPageImage (taskId: string, pageNumber: number): Promise<Buffer> {
    const response = await this.request(
      `/api/tasks/${encodeURIComponent(taskId)}/page/${pageNumber}`,
      { method: 'GET' },
    )
    return Buffer.from(await response.arrayBuffer())
  }

  /** List the authenticated user's tasks (paginated). */
  async getUserTasks (page = 1, pageSize = 10): Promise<PaginatedTasks> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) })
    const response = await this.request(`/api/tasks/user/?${params}`, { method: 'GET' })
    return (await response.json()) as PaginatedTasks
  }

  /** Get global and per-user task statistics. */
  async getTaskStats (page = 1, pageSize = 10): Promise<TaskStats> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) })
    const response = await this.request(`/api/stats/tasks?${params}`, { method: 'GET' })
    return (await response.json()) as TaskStats
  }

  /** Count distinct users who created a task today. */
  async getUsersCountToday (): Promise<number> {
    const response = await this.request('/api/users/count-users-today', { method: 'GET' })
    const { users_today: usersToday } = (await response.json()) as { users_today: number }
    return usersToday
  }

  /** Delete a task (and its stored result) by ID. */
  async deleteTask (taskId: string): Promise<void> {
    await this.request(`/api/tasks/${encodeURIComponent(taskId)}`, { method: 'DELETE' })
  }

  /** Bulk-delete tasks in a date range with a given status (admin only). */
  async deleteTasksByDateAndStatus (startDate: Date, endDate: Date, status: TaskStatus): Promise<void> {
    const params = new URLSearchParams({
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString(),
      status,
    })
    await this.request(`/api/v1/tasks/?${params}`, { method: 'DELETE' })
  }

  /** Get extracted text from a completed task. */
  async getTaskText (taskId: string): Promise<string> {
    const response = await this.request(`/api/text-task/${encodeURIComponent(taskId)}`, { method: 'GET' })
    return response.text()
  }

  /**
   * Get a task's output in a chosen shape: `"text"` (default, plain text), `"form"`
   * (per-page form entries, JSON), `"form-csv"` (form entries as CSV bytes), or
   * `"only-result"` (raw OCR result, JSON).
   */
  async getTaskValue (taskId: string, transform: TaskValueTransform = 'text'): Promise<string | Buffer | unknown> {
    const params = new URLSearchParams({ transform })
    const response = await this.request(`/api/task-to-value/${encodeURIComponent(taskId)}?${params}`, { method: 'GET' })
    if (transform === 'form-csv') {
      return Buffer.from(await response.arrayBuffer())
    }
    if (transform === 'text') {
      return response.text()
    }
    return response.json()
  }

  /**
   * Upload a document and block until OCR completes (or times out) - the
   * OpenWebUI-style one-shot endpoint (`PUT /api/process`), as opposed to
   * `createJob` + `waitForTask`, which give you the intermediate `TaskModel`.
   */
  async processDocument (filePath: string, options: ProcessDocumentOptions = {}): Promise<ProcessResponse[]> {
    const data = await readFile(filePath)
    const maxWaitTimeSeconds = options.maxWaitTimeSeconds ?? 300
    const pollIntervalSeconds = options.pollIntervalSeconds ?? 2

    const response = await this.request(
      '/api/process',
      {
        method: 'PUT',
        body: new Uint8Array(data),
        headers: {
          'max_wait_time': String(maxWaitTimeSeconds),
          'poll_interval': String(pollIntervalSeconds),
          'X-Filename': basename(filePath),
          'Content-Type': options.mimeType ?? guessMimeType(filePath),
        },
      },
      { timeoutMs: Math.max(this.timeoutMs, (maxWaitTimeSeconds + 10) * 1000) },
    )
    return (await response.json()) as ProcessResponse[]
  }

  /** Poll a task until it completes, fails, or `maxWaitTimeMs` elapses. */
  async waitForTask (taskId: string, options: WaitForTaskOptions = {}): Promise<TaskModel> {
    const pollIntervalMs = options.pollIntervalMs ?? 2000
    const maxWaitTimeMs = options.maxWaitTimeMs ?? 300_000

    let elapsedMs = 0
    while (elapsedMs < maxWaitTimeMs) {
      const task = await this.getTask(taskId)

      if (task.status === 'completed') {
        return task
      }
      if (task.status === 'failed') {
        const error = (task.extras?.error as string | undefined) ?? 'Unknown error'
        throw new OCRAPIError(500, `Task failed: ${error}`)
      }

      await new Promise(resolve => setTimeout(resolve, pollIntervalMs))
      elapsedMs += pollIntervalMs
    }

    throw new OCRTimeoutError(`Task ${taskId} did not complete within ${maxWaitTimeMs}ms`)
  }
}
