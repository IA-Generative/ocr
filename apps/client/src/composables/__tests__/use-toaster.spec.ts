import type useToaster from '@/composables/use-toaster'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

type Toaster = ReturnType<typeof useToaster>

// `use-toaster` keeps its message list in module scope, so every test needs a
// fresh copy of the module rather than a fresh call to the composable.
async function freshToaster (defaultTimeout?: number): Promise<Toaster> {
  vi.resetModules()
  const { default: factory } = await import('@/composables/use-toaster')
  return defaultTimeout === undefined
    ? factory()
    : factory(defaultTimeout)
}

describe('useToaster', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('addMessage', () => {
    it('fills in the defaults a caller omitted', async () => {
      const { messages, addMessage } = await freshToaster()

      addMessage({ description: 'Traitement lancé' })

      expect(messages).toHaveLength(1)
      expect(messages[0]).toMatchObject({
        description: 'Traitement lancé',
        type: 'info',
        titleTag: 'h3',
        closeable: true,
        timeout: 10000,
      })
      expect(messages[0]?.id).toMatch(/^toaster-[a-z0-9]{5}$/)
    })

    it('honours the timeout the composable was configured with', async () => {
      const { messages, addMessage } = await freshToaster(500)

      addMessage({ description: 'court' })

      expect(messages[0]?.timeout).toBe(500)
    })

    it('evicts the message once its timeout elapses', async () => {
      const { messages, addMessage } = await freshToaster(500)

      addMessage({ description: 'éphémère' })
      expect(messages).toHaveLength(1)

      vi.advanceTimersByTime(499)
      expect(messages).toHaveLength(1)

      vi.advanceTimersByTime(1)
      expect(messages).toHaveLength(0)
    })

    it('replaces an existing message that reuses the same id', async () => {
      const { messages, addMessage } = await freshToaster()

      addMessage({ id: 'upload', description: 'Envoi en cours' })
      addMessage({ id: 'upload', description: 'Envoi terminé' })

      expect(messages).toHaveLength(1)
      expect(messages[0]?.description).toBe('Envoi terminé')
    })

    it('does not evict a replaced message when the original timeout fires', async () => {
      const { messages, addMessage } = await freshToaster(500)

      addMessage({ id: 'upload', description: 'Envoi en cours' })
      vi.advanceTimersByTime(400)
      addMessage({ id: 'upload', description: 'Envoi terminé' })

      // The first message's timer would have fired here had it not been cleared.
      vi.advanceTimersByTime(100)

      expect(messages).toHaveLength(1)
      expect(messages[0]?.description).toBe('Envoi terminé')
    })

    it('coerces a non-string description', async () => {
      const { messages, addMessage } = await freshToaster()

      addMessage({ description: 42 as unknown as string })

      expect(messages[0]?.description).toBe('42')
    })
  })

  describe('addSuccessMessage / addErrorMessage', () => {
    it('tags the message with the matching type', async () => {
      const { messages, addSuccessMessage, addErrorMessage } = await freshToaster()

      addSuccessMessage({ description: 'ok' })
      addErrorMessage({ description: 'ko' })

      expect(messages.map(m => m.type)).toEqual(['success', 'error'])
    })

    it('accepts a bare string as shorthand for a description', async () => {
      const { messages, addSuccessMessage } = await freshToaster()

      addSuccessMessage('Tâche terminée')

      expect(messages[0]).toMatchObject({ description: 'Tâche terminée', type: 'success' })
    })
  })

  describe('removeMessage', () => {
    it('removes the matching message and leaves the others alone', async () => {
      const { messages, addMessage, removeMessage } = await freshToaster()

      addMessage({ id: 'a', description: 'un' })
      addMessage({ id: 'b', description: 'deux' })

      removeMessage('a')

      expect(messages.map(m => m.id)).toEqual(['b'])
    })

    it('is a no-op for an unknown id', async () => {
      const { messages, addMessage, removeMessage } = await freshToaster()

      addMessage({ id: 'a', description: 'un' })
      removeMessage('nope')

      expect(messages).toHaveLength(1)
    })
  })

  it('generates ids from the full alphabet', async () => {
    const { messages, addMessage } = await freshToaster()

    for (let i = 0; i < 400; i++) {
      addMessage({ description: `m${i}` })
    }

    // Regression guard: the alphabet used to be missing 'x'.
    const generated = messages.map(m => m.id).join('')
    expect(generated).toMatch(/x/)
  })

  it('treats timeout: 0 as immediate eviction, not "never expire"', async () => {
    const { messages, addMessage } = await freshToaster()

    addMessage({ description: 'file d\'attente', timeout: 0 })
    expect(messages).toHaveLength(1)

    vi.advanceTimersByTime(0)

    // `message.timeout ??= defaultTimeout` leaves an explicit 0 in place, so the
    // message is dropped on the next tick. Callers passing 0 to mean "keep this
    // one on screen" (see the queue notice in stores/ocr.ts) do not get that.
    expect(messages).toHaveLength(0)
  })
})
