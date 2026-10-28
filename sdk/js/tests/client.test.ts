import type { TaskModel } from '../src/types.js'
import { mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest'
import { OCRClient } from '../src/client.js'
import { OCRAPIError, OCRAuthenticationError, OCRTimeoutError } from '../src/errors.js'

function jsonResponse (body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
}

function makeTask (overrides: Partial<TaskModel> = {}): TaskModel {
  return {
    id: 'task-1',
    user_id: 'user-1',
    type: 'default',
    status: 'queued',
    created_at: 0,
    updated_at: 0,
    ...overrides,
  }
}

describe('ocrClient', () => {
  let fetchMock: ReturnType<typeof vi.fn>

  beforeEach(() => {
    fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('getHealth sends a GET and parses the response', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({
      name: 'ocr-api',
      version: '1.0',
      up_time: '1s',
      status: 'healthy',
    }))

    const client = new OCRClient('http://localhost:5000')
    const health = await client.getHealth()

    expect(health.status).toBe('healthy')
    const [url, init] = fetchMock.mock.calls[0]!
    expect(url).toBe('http://localhost:5000/api/health')
    expect(init.method).toBe('GET')
  })

  it('sends the api key as a bearer token', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({ name: 'x', version: '1', up_time: '1s' }))

    const client = new OCRClient('http://localhost:5000', { apiKey: 'secret-key' })
    await client.getHealth()

    const [, init] = fetchMock.mock.calls[0]!
    const headers = new Headers(init.headers)
    expect(headers.get('Authorization')).toBe('Bearer secret-key')
  })

  it('strips a trailing slash from baseUrl', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({ name: 'x', version: '1', up_time: '1s' }))

    const client = new OCRClient('http://localhost:5000/')
    await client.getHealth()

    const [url] = fetchMock.mock.calls[0]!
    expect(url).toBe('http://localhost:5000/api/health')
  })

  it('throws OCRAPIError on a non-2xx response', async () => {
    fetchMock.mockResolvedValueOnce(new Response('not found', { status: 404 }))

    const client = new OCRClient('http://localhost:5000')

    await expect(client.getTask('missing')).rejects.toMatchObject({
      constructor: OCRAPIError,
      statusCode: 404,
      body: 'not found',
    })
  })

  it('throws OCRTimeoutError when the request aborts', async () => {
    fetchMock.mockImplementationOnce((_url: string, init: RequestInit) => new Promise((_resolve, reject) => {
      init.signal?.addEventListener('abort', () => {
        const err = new Error('aborted')
        err.name = 'AbortError'
        reject(err)
      })
    }))

    const client = new OCRClient('http://localhost:5000', { timeoutMs: 10 })

    await expect(client.getHealth()).rejects.toBeInstanceOf(OCRTimeoutError)
  })

  it('login() authenticates via POST /api/auth/token and stores the access token', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({ access_token: 'tok-123', expires_in: 300, token_type: 'Bearer' }))
    fetchMock.mockResolvedValueOnce(jsonResponse({ name: 'x', version: '1', up_time: '1s' }))

    const client = new OCRClient('http://localhost:5000')
    await client.login('user@example.com', 'hunter2')

    const [loginUrl, loginInit] = fetchMock.mock.calls[0]!
    expect(loginUrl).toBe('http://localhost:5000/api/auth/token')
    expect(loginInit.method).toBe('POST')
    expect(JSON.parse(loginInit.body as string)).toEqual({ username: 'user@example.com', password: 'hunter2' })

    await client.getHealth()
    const [, healthInit] = fetchMock.mock.calls[1]!
    const headers = new Headers(healthInit.headers)
    expect(headers.get('Authorization')).toBe('Bearer tok-123')
  })

  it('login() wraps a rejected credential exchange in OCRAuthenticationError', async () => {
    fetchMock.mockResolvedValueOnce(new Response('invalid credentials', { status: 401 }))

    const client = new OCRClient('http://localhost:5000')

    await expect(client.login('user@example.com', 'wrong')).rejects.toBeInstanceOf(OCRAuthenticationError)
  })

  it('a 401 triggers a silent refresh and retries the original request once', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({ access_token: 'tok-1', refresh_token: 'refresh-1', expires_in: 300 }))
    fetchMock.mockResolvedValueOnce(new Response('expired', { status: 401 }))
    fetchMock.mockResolvedValueOnce(jsonResponse({ access_token: 'tok-2', refresh_token: 'refresh-2', expires_in: 300 }))
    fetchMock.mockResolvedValueOnce(jsonResponse(makeTask({ status: 'queued' })))

    const client = new OCRClient('http://localhost:5000')
    await client.login('user@example.com', 'hunter2')

    const task = await client.getTask('task-1')

    expect(task.status).toBe('queued')
    expect(fetchMock).toHaveBeenCalledTimes(4)
    const [refreshUrl, refreshInit] = fetchMock.mock.calls[2]!
    expect(refreshUrl).toBe('http://localhost:5000/api/auth/refresh')
    expect(JSON.parse(refreshInit.body as string)).toEqual({ refresh_token: 'refresh-1' })
    const [, retryInit] = fetchMock.mock.calls[3]!
    const headers = new Headers(retryInit.headers)
    expect(headers.get('Authorization')).toBe('Bearer tok-2')
  })

  it('a 401 with no refresh token available surfaces as OCRAPIError, no retry', async () => {
    fetchMock.mockResolvedValueOnce(new Response('unauthorized', { status: 401 }))

    const client = new OCRClient('http://localhost:5000', { apiKey: 'static-key' })

    await expect(client.getTask('task-1')).rejects.toMatchObject({ constructor: OCRAPIError, statusCode: 401 })
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('a 401 with an expired refresh token surfaces the original 401, no infinite loop', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({ access_token: 'tok-1', refresh_token: 'refresh-1', expires_in: 300 }))
    fetchMock.mockResolvedValueOnce(new Response('expired', { status: 401 }))
    fetchMock.mockResolvedValueOnce(new Response('invalid refresh token', { status: 401 }))

    const client = new OCRClient('http://localhost:5000')
    await client.login('user@example.com', 'hunter2')

    await expect(client.getTask('task-1')).rejects.toMatchObject({ constructor: OCRAPIError, statusCode: 401 })
    expect(fetchMock).toHaveBeenCalledTimes(3)
  })

  it('refresh() updates the stored tokens', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({ access_token: 'tok-1', refresh_token: 'refresh-1', expires_in: 300 }))
    fetchMock.mockResolvedValueOnce(jsonResponse({ access_token: 'tok-2', refresh_token: 'refresh-2', expires_in: 300 }))
    fetchMock.mockResolvedValueOnce(jsonResponse({ name: 'x', version: '1', up_time: '1s' }))

    const client = new OCRClient('http://localhost:5000')
    await client.login('user@example.com', 'hunter2')
    await client.refresh()
    await client.getHealth()

    const [, healthInit] = fetchMock.mock.calls[2]!
    const headers = new Headers(healthInit.headers)
    expect(headers.get('Authorization')).toBe('Bearer tok-2')
  })

  it('refresh() throws OCRAuthenticationError when no refresh token is available', async () => {
    const client = new OCRClient('http://localhost:5000', { apiKey: 'static-key' })

    await expect(client.refresh()).rejects.toBeInstanceOf(OCRAuthenticationError)
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('getUserTasks() encodes pagination params and returns the paginated envelope', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse({
      total: 1,
      page: 2,
      page_size: 5,
      items: [
        makeTask(),
      ],
    }))

    const client = new OCRClient('http://localhost:5000')
    const result = await client.getUserTasks(2, 5)

    expect(result.total).toBe(1)
    expect(result.items).toHaveLength(1)
    const [url] = fetchMock.mock.calls[0]!
    expect(url).toBe('http://localhost:5000/api/tasks/user/?page=2&page_size=5')
  })

  it('deleteTask() sends a DELETE request', async () => {
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }))

    const client = new OCRClient('http://localhost:5000')
    await client.deleteTask('task-1')

    const [url, init] = fetchMock.mock.calls[0]!
    expect(url).toBe('http://localhost:5000/api/tasks/task-1')
    expect(init.method).toBe('DELETE')
  })

  it('deleteTasksByDateAndStatus() sends ISO dates and the status as query params', async () => {
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }))

    const client = new OCRClient('http://localhost:5000')
    const start = new Date('2026-01-01T00:00:00.000Z')
    const end = new Date('2026-01-02T00:00:00.000Z')
    await client.deleteTasksByDateAndStatus(start, end, 'failed')

    const [url] = fetchMock.mock.calls[0]!
    const parsed = new URL(url as string)
    expect(parsed.searchParams.get('start_date')).toBe(start.toISOString())
    expect(parsed.searchParams.get('end_date')).toBe(end.toISOString())
    expect(parsed.searchParams.get('status')).toBe('failed')
  })

  it('getTaskPageImage() returns a Buffer', async () => {
    const bytes = new Uint8Array([1, 2, 3, 4])
    fetchMock.mockResolvedValueOnce(new Response(bytes, { status: 200 }))

    const client = new OCRClient('http://localhost:5000')
    const buf = await client.getTaskPageImage('task-1', 1)

    expect(Buffer.isBuffer(buf)).toBe(true)
    expect([...buf]).toEqual([1, 2, 3, 4])
  })

  it('getTaskValue() parses "text" as plain text and "only-result" as JSON', async () => {
    fetchMock.mockResolvedValueOnce(new Response('hello world', { status: 200 }))
    const client = new OCRClient('http://localhost:5000')
    expect(await client.getTaskValue('task-1', 'text')).toBe('hello world')

    fetchMock.mockResolvedValueOnce(jsonResponse({ type: 'ocr' }))
    expect(await client.getTaskValue('task-1', 'only-result')).toEqual({ type: 'ocr' })
  })

  it('getTaskValue() returns a Buffer for "form-csv"', async () => {
    fetchMock.mockResolvedValueOnce(new Response('key,value\na,b\n', { status: 200 }))

    const client = new OCRClient('http://localhost:5000')
    const buf = await client.getTaskValue('task-1', 'form-csv')

    expect(Buffer.isBuffer(buf)).toBe(true)
    expect((buf as Buffer).toString()).toBe('key,value\na,b\n')
  })

  it('waitForTask() polls until the task completes', async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse(makeTask({ status: 'queued' })))
      .mockResolvedValueOnce(jsonResponse(makeTask({ status: 'in_progress' })))
      .mockResolvedValueOnce(jsonResponse(makeTask({ status: 'completed' })))

    const client = new OCRClient('http://localhost:5000')
    const result = await client.waitForTask('task-1', { pollIntervalMs: 0 })

    expect(result.status).toBe('completed')
    expect(fetchMock).toHaveBeenCalledTimes(3)
  })

  it('waitForTask() throws OCRAPIError when the task fails', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(makeTask({
      status: 'failed',
      extras: { error: 'boom' },
    })))

    const client = new OCRClient('http://localhost:5000')

    await expect(client.waitForTask('task-1', { pollIntervalMs: 0 })).rejects.toMatchObject({
      constructor: OCRAPIError,
      message: expect.stringContaining('boom'),
    })
  })

  it('waitForTask() throws OCRTimeoutError once maxWaitTimeMs elapses', async () => {
    fetchMock.mockImplementation(async () => jsonResponse(makeTask({ status: 'queued' })))

    const client = new OCRClient('http://localhost:5000')

    await expect(
      client.waitForTask('task-1', { pollIntervalMs: 1, maxWaitTimeMs: 3 }),
    ).rejects.toBeInstanceOf(OCRTimeoutError)
  })
})

describe('ocrClient file uploads', () => {
  let dir: string
  let filePath: string
  let fetchMock: ReturnType<typeof vi.fn>

  beforeAll(async () => {
    dir = await mkdtemp(join(tmpdir(), 'ocr-sdk-test-'))
    filePath = join(dir, 'document.pdf')
    await writeFile(filePath, 'fake-pdf-bytes')
  })

  beforeEach(() => {
    fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  afterAll(async () => {
    await rm(dir, { recursive: true, force: true })
  })

  it('createJob() uploads the file as multipart form data', async () => {
    fetchMock.mockResolvedValueOnce(new Response(JSON.stringify(makeTask({ status: 'queued' })), {
      status: 201,
      headers: { 'Content-Type': 'application/json' },
    }))

    const client = new OCRClient('http://localhost:5000')
    const task = await client.createJob(filePath, { groupId: 'MY_GROUP' })

    expect(task.status).toBe('queued')
    const [url, init] = fetchMock.mock.calls[0]!
    expect(url).toBe('http://localhost:5000/api/jobs/')
    expect(init.method).toBe('POST')
    const form = init.body as FormData
    expect(form.get('group_id')).toBe('MY_GROUP')
    expect(form.get('task_operation')).toBe('default')
    const file = form.get('file') as File
    expect(file.name).toBe('document.pdf')
  })

  it('processDocument() sends the raw file body with the upload headers', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse([
      { page_content: 'hello', metadata: {} },
    ]))

    const client = new OCRClient('http://localhost:5000')
    const results = await client.processDocument(filePath, { maxWaitTimeSeconds: 5, pollIntervalSeconds: 1 })

    expect(results).toHaveLength(1)
    const [url, init] = fetchMock.mock.calls[0]!
    expect(url).toBe('http://localhost:5000/api/process')
    expect(init.method).toBe('PUT')
    const headers = new Headers(init.headers)
    expect(headers.get('X-Filename')).toBe('document.pdf')
    expect(headers.get('max_wait_time')).toBe('5')
    expect(headers.get('poll_interval')).toBe('1')
  })
})
