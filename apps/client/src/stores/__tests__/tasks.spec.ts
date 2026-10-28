import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useTasksStore } from '@/stores/tasks'

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

describe('tasks store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('fetchUserTasks', () => {
    it('maps the paginated payload onto the store', async () => {
      http.get.mockResolvedValue({
        data: {
          items: [
            { id: 'a' },
            { id: 'b' },
          ],
          page: 2,
          page_size: 25,
          total: 42,
        },
      })
      const store = useTasksStore()

      await store.fetchUserTasks(2, 25)

      expect(http.get).toHaveBeenCalledWith('/tasks/user/', {
        params: { page: 2, page_size: 25 },
      })
      expect(store.userTasksPaginated).toMatchObject({ page: 2, page_size: 25, total: 42 })
      expect(store.userTasksPaginated.items).toHaveLength(2)
    })

    it('defaults to the first page', async () => {
      http.get.mockResolvedValue({
        data: {
          items: [],
          page: 1,
          page_size: 10,
          total: 0,
        },
      })

      await useTasksStore().fetchUserTasks()

      expect(http.get).toHaveBeenCalledWith('/tasks/user/', {
        params: { page: 1, page_size: 10 },
      })
    })

    it('falls back to the requested paging when the API omits it', async () => {
      http.get.mockResolvedValue({ data: {} })
      const store = useTasksStore()

      await store.fetchUserTasks(3, 50)

      expect(store.userTasksPaginated).toMatchObject({
        page: 3,
        page_size: 50,
        total: 0,
        items: [],
      })
    })

    it('clears the loading flag even when the request fails', async () => {
      http.get.mockRejectedValue(new Error('boom'))
      const store = useTasksStore()

      await store.fetchUserTasks()

      expect(store.loading).toBe(false)
    })

    it('holds loading true for the duration of the request', async () => {
      let release: (v: unknown) => void = () => {}
      http.get.mockReturnValue(new Promise((resolve) => { release = resolve }))
      const store = useTasksStore()

      const pending = store.fetchUserTasks()
      expect(store.loading).toBe(true)

      release({
        data: { items: [] },
      })
      await pending
      expect(store.loading).toBe(false)
    })
  })

  describe('deleteTask', () => {
    beforeEach(() => {
      http.get.mockResolvedValue({
        data: {
          items: [
            { id: 'a' },
            { id: 'b' },
          ],
          page: 1,
          page_size: 10,
          total: 2,
        },
      })
    })

    it('drops the task locally and decrements the total', async () => {
      const store = useTasksStore()
      await store.fetchUserTasks()
      http.delete.mockResolvedValue({})

      await store.deleteTask('a')

      expect(http.delete).toHaveBeenCalledWith('/tasks/a')
      expect(store.userTasksPaginated.items.map((t: { id: string }) => t.id)).toEqual(['b'])
      expect(store.userTasksPaginated.total).toBe(1)
    })

    it('percent-encodes the id it puts in the path', async () => {
      http.delete.mockResolvedValue({})

      await useTasksStore().deleteTask('a b/c')

      expect(http.delete).toHaveBeenCalledWith('/tasks/a%20b%2Fc')
    })

    it('never drives the total below zero', async () => {
      const store = useTasksStore()
      http.delete.mockResolvedValue({})

      await store.deleteTask('ghost')

      expect(store.userTasksPaginated.total).toBe(0)
    })

    it('rejects an empty id without calling the API', async () => {
      await expect(useTasksStore().deleteTask('')).rejects.toThrow('taskId required')

      expect(http.delete).not.toHaveBeenCalled()
    })

    it('re-throws so the caller can react, and leaves the list untouched', async () => {
      const store = useTasksStore()
      await store.fetchUserTasks()
      http.delete.mockRejectedValue(new Error('403 Forbidden'))

      await expect(store.deleteTask('a')).rejects.toThrow('403 Forbidden')

      expect(store.userTasksPaginated.items).toHaveLength(2)
    })
  })
})
