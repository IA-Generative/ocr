import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import createHttpClient from '@/api/http-client'

const { login } = vi.hoisted(() => ({
  login: vi.fn(),
}))

vi.mock('@/utils/auth', () => ({ login }))

function httpError (config: InternalAxiosRequestConfig, status: number) {
  return Object.assign(new Error(`Request failed with status code ${status}`), {
    config,
    isAxiosError: true,
    response: {
      status,
      data: {},
      statusText: '',
      headers: {},
      config,
    },
  })
}

function withTransport (client: AxiosInstance, handler: (config: InternalAxiosRequestConfig) => unknown) {
  client.defaults.adapter = async (config) => {
    const result = await handler(config as InternalAxiosRequestConfig)
    return {
      data: result,
      status: 200,
      statusText: 'OK',
      headers: {},
      config,
    } as never
  }
}

describe('createHttpClient', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('sends cookies but no Authorization header - the browser holds no Keycloak token in the BFF flow', async () => {
    const client = createHttpClient('http://api.test')
    withTransport(client, config => config.headers.Authorization ?? null)

    const { data } = await client.get('/health')

    expect(data).toBeNull()
    expect(client.defaults.withCredentials).toBe(true)
  })

  describe('401 handling', () => {
    it('redirects to the backend login endpoint and rejects', async () => {
      const client = createHttpClient('http://api.test')
      client.defaults.adapter = (async (config: InternalAxiosRequestConfig) => {
        throw httpError(config, 401)
      }) as never

      await expect(client.get('/tasks')).rejects.toThrow('status code 401')

      expect(login).toHaveBeenCalledOnce()
    })
  })

  it('lets non-401 failures through without touching the session', async () => {
    const client = createHttpClient('http://api.test')
    client.defaults.adapter = (async (config: InternalAxiosRequestConfig) => {
      throw httpError(config, 500)
    }) as never

    await expect(client.get('/tasks')).rejects.toThrow('status code 500')

    expect(login).not.toHaveBeenCalled()
  })
})
