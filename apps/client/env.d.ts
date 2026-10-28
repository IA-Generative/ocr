/// <reference types="vite/client" />

declare const __APP_VERSION__: string

// CSS entry point reached through the package's `exports` map; TypeScript 6 reports it
// as an unresolved side-effect import without this declaration.
declare module '@gouvminint/vue-dsfr/styles'

declare module 'virtual:pwa-register/vue' {
  import type { Ref } from 'vue'

  export interface RegisterSWOptions {
    immediate?: boolean
    onNeedRefresh?: () => void
    onOfflineReady?: () => void
    onRegistered?: (registration: ServiceWorkerRegistration | undefined) => void
    onRegisterError?: (error: any) => void
  }

  export function useRegisterSW (options?: RegisterSWOptions): {
    needRefresh: Ref<boolean>
    offlineReady: Ref<boolean>
    updateServiceWorker: (reloadPage?: boolean) => Promise<void>
  }
}
