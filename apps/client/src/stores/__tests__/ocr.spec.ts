import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useOcrStore } from '@/stores/ocr'

const { http } = vi.hoisted(() => ({
  http: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

vi.mock('@/api/http-client', () => ({
  default: () => http,
}))

function fileOf (type: string, size = 1024, name = 'document.pdf') {
  const file = new File(['x'], name, { type })
  Object.defineProperty(file, 'size', { value: size })
  return file
}

const MB = 1024 * 1024

describe('ocr store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('validateFile', () => {
    it.each([
      ['application/pdf'],
      ['image/jpeg'],
      ['image/png'],
      ['text/csv'],
      ['application/zip'],
      ['application/vnd.oasis.opendocument.text'],
    ])('accepts %s', (mime) => {
      expect(useOcrStore().validateFile(fileOf(mime))).toEqual({ valid: true })
    })

    it('rejects a type outside the allow-list and names it', () => {
      const result = useOcrStore().validateFile(fileOf('application/x-msdownload'))

      expect(result.valid).toBe(false)
      expect(result.message).toContain('application/x-msdownload')
    })

    it('rejects an empty mime type rather than letting it through', () => {
      expect(useOcrStore().validateFile(fileOf('')).valid).toBe(false)
    })

    it('accepts a file sitting exactly on the 200 Mo limit', () => {
      expect(useOcrStore().validateFile(fileOf('application/pdf', 200 * MB))).toEqual({ valid: true })
    })

    it('rejects a file one byte over the limit and reports its size', () => {
      const result = useOcrStore().validateFile(fileOf('application/pdf', 200 * MB + 1))

      expect(result.valid).toBe(false)
      expect(result.message).toContain('200.00 Mo')
    })
  })

  describe('pollTask', () => {
    it('settles on a completed task and stops polling', async () => {
      http.get.mockResolvedValue({
        data: { id: 't1', status: 'completed' },
      })
      const store = useOcrStore()

      await store.pollTask('t1', 0)

      expect(store.status).toBe('completed')
      expect(store.isPolling).toBe(false)
      expect(http.get).toHaveBeenCalledTimes(1)
    })

    it('keeps polling through in_progress and records the percentage', async () => {
      http.get
        .mockResolvedValueOnce({
          data: { id: 't1', status: 'in_progress', percentage: 40 },
        })
        .mockResolvedValueOnce({
          data: { id: 't1', status: 'completed' },
        })
      const store = useOcrStore()

      await store.pollTask('t1', 0)

      expect(http.get).toHaveBeenCalledTimes(2)
      expect(store.status).toBe('completed')
      expect(store.isPolling).toBe(false)
    })

    it('surfaces the API error message when the task fails', async () => {
      http.get.mockResolvedValue({
        data: {
          id: 't1',
          status: 'failed',
          extras: { error: 'OCR engine crashed' },
        },
      })
      const store = useOcrStore()

      await store.pollTask('t1', 0)

      expect(store.error).toBe('OCR engine crashed')
      expect(store.isPolling).toBe(false)
    })

    it('falls back to a generic message when the failure carries no detail', async () => {
      http.get.mockResolvedValue({
        data: { id: 't1', status: 'failed' },
      })
      const store = useOcrStore()

      await store.pollTask('t1', 0)

      expect(store.error).toBe('Le traitement OCR a échoué')
    })

    it('reports the caller position while queued', async () => {
      http.get
        .mockResolvedValueOnce({
          data: { id: 't1', status: 'queued', position: 2 },
        })
        .mockResolvedValueOnce({
          data: { id: 't1', status: 'completed' },
        })
      const store = useOcrStore()

      await store.pollTask('t1', 0)

      expect(store.position).toBe(3)
    })

    it('stops when the request itself throws', async () => {
      http.get.mockRejectedValue(new Error('network down'))
      const store = useOcrStore()

      await store.pollTask('t1', 0)

      expect(store.isPolling).toBe(false)
      expect(store.error).toContain('network down')
    })
  })

  describe('stopPolling', () => {
    it('interrupts a poll that would otherwise never finish', async () => {
      const store = useOcrStore()
      let polls = 0
      http.get.mockImplementation(async () => {
        polls += 1
        if (polls === 3) {
          store.stopPolling()
        }
        return {
          data: { id: 't1', status: 'in_progress', percentage: polls * 10 },
        }
      })

      await store.pollTask('t1', 0)

      expect(polls).toBe(3)
      expect(store.isPolling).toBe(false)
    })

    it('is safe to call when nothing is polling', () => {
      const store = useOcrStore()

      expect(() => store.stopPolling()).not.toThrow()
      expect(store.isPolling).toBe(false)
    })

    it('lets reset() halt an in-flight poll too', async () => {
      const store = useOcrStore()
      let polls = 0
      http.get.mockImplementation(async () => {
        polls += 1
        if (polls === 2) {
          store.reset()
        }
        return {
          data: { id: 't1', status: 'in_progress' },
        }
      })

      await store.pollTask('t1', 0)

      expect(polls).toBe(2)
      expect(store.isPolling).toBe(false)
    })
  })
})
