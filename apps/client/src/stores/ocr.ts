/**
 *
 * @Status - Errors :
 *    - CREATED = "created"  # Tâche instanciée mais pas encore mise en file
 *    - QUEUED = "queued"  # En attente dans une file de traitement
 *    - STARTED = "started"  # A commencé à être traitée
 *    - IN_PROGRESS = "in_progress"
 *    - COMPLETED = "completed"  # Traitée avec succès
 *    - FAILED = "failed"  # Erreur fatale
 *    - RETRYING = "retrying"  # En cours de nouvelle tentative après échec
 *    - CANCELED = "canceled"  # Annulée manuellement ou par logique métier
 *    - TIMEOUT = "timeout"  # N’a pas pu terminer dans le temps imparti
 *
 */
import type { components } from '@/api/types/api.schema'

import { defineStore } from 'pinia'
import { ref } from 'vue'
import useToaster from '@/composables/use-toaster'
import createHttpClient from './../api/http-client'
import { OCR_API_URL } from './../utils/constants'

type TaskModel = components['schemas']['TaskModel']

const { addErrorMessage, addSuccessMessage } = useToaster()

const http = createHttpClient(OCR_API_URL)

const VALID_MIME_TYPES = [
  'application/pdf',
  'image/jpeg',
  'image/png',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // docx
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // xlsx
  'application/vnd.oasis.opendocument.text', // odt
  'application/vnd.oasis.opendocument.spreadsheet', // ods
  'application/vnd.oasis.opendocument.presentation', // odp
  'text/csv',
  'message/rfc822', // eml
  'application/zip', // zip
  'application/x-zip-compressed', // zip
]

export const useOcrStore = defineStore('ocr', () => {
  const status = ref<string | null>(null)
  const percentage = ref<number>(0)
  const taskData = ref<TaskModel | null>(null)
  const isPolling = ref(false)
  const error = ref<string | undefined>(undefined)
  const processingState = ref<'idle' | 'validating' | 'uploading' | 'processing'>('idle')
  const position = ref<number | null>(null)
  const originalFileName = ref<string | null>(null)
  const previousPosition = ref<number | null>(null)

  async function healthCheck (): Promise<boolean> {
    try {
      processingState.value = 'validating'
      const { data } = await http.get<{ status: string }>('/health')
      if (data.status !== 'healthy') {
        throw new Error(`Statut inattendu: ${data.status}`)
      }
      return true
    } catch (err: any) {
      error.value = err.message ?? 'Erreur inconnue lors du health check.'
      return false
    } finally {
      if (processingState.value === 'validating') {
        processingState.value = 'idle'
      }
    }
  }

  async function getTask (taskId: string): Promise<TaskModel> {
    try {
      const { data } = await http.get<TaskModel>(`/tasks/${taskId}`)
      return data
    } catch (err: any) {
      addErrorMessage({
        title: 'Erreur :',
        description: `Erreur lors de la récupération de la tâche ${taskId}: ${err}`,
      })
      throw new Error(`Impossible de récupérer l'état de la tâche: ${err.message ?? 'Erreur inconnue'}`)
    }
  }

  async function getPageImageUrl (taskId: string, pageNumber: number): Promise<string> {
    const { data } = await http.get<Blob>(`/tasks/${taskId}/page/${pageNumber}`, { responseType: 'blob' })
    return URL.createObjectURL(data)
  }

  async function pollTask (
    taskId: string,
    intervalMs = 2000,
  ) {
    status.value = null
    percentage.value = 0
    taskData.value = null
    error.value = undefined
    isPolling.value = true
    processingState.value = 'processing'
    previousPosition.value = null

    try {
      // A loop rather than recursion: `check()` used to await itself, so the
      // promise chain grew for the whole lifetime of a job and there was no way
      // to interrupt it. Re-reading `isPolling` each turn makes the poll
      // cancellable — see `stopPolling()`.
      while (isPolling.value) {
        const task = await getTask(taskId)

        status.value = task.status

        switch (task.status) {
          case 'in_progress':
            status.value = task.status
            percentage.value = task.percentage || 0
            taskData.value = task
            break

          case 'completed':
            addSuccessMessage({
              title: 'Tâche terminée avec succès :',
              description: 'Vous pouvez accéder au résultat.',
            })
            status.value = task.status
            taskData.value = task
            isPolling.value = false
            processingState.value = 'idle'
            return

          case 'failed':
            addErrorMessage({
              title: 'Échec du traitement :',
              description: 'Une erreur est survenue lors du traitement OCR.',
            })
            error.value = typeof task?.extras?.error === 'string'
              ? task.extras.error
              : 'Le traitement OCR a échoué'
            isPolling.value = false
            processingState.value = 'idle'
            return

          case 'queued': {
            const currentPosition = (task.position ?? 0) + 1
            position.value = currentPosition

            if (previousPosition.value !== currentPosition) {
              addSuccessMessage({
                title: 'Vous êtes en file d\'attente :',
                description: `Il y a ${position.value} document(s) en attente.`,
                timeout: 0,
              })
              previousPosition.value = currentPosition
            }

            status.value = task.status
            break
          }

          default:
            break
        }

        await new Promise(res => setTimeout(res, intervalMs))
      }
    } catch (err: any) {
      error.value = err.message ?? 'Erreur inconnue lors du polling.'
      isPolling.value = false
      processingState.value = 'idle'
    }
  }

  /**
   * Vérifie le type de fichier avant envoi
   */
  function validateFile (file: File): { valid: boolean, message?: string } {
    // Vérification du type MIME
    if (!VALID_MIME_TYPES.includes(file.type)) {
      return {
        valid: false,
        message: `Type de fichier non supporté: ${file.type}. Utilisez PDF, JPEG, PNG, DOCX, XLSX, ODT, ODS, ODP, CSV, EML ou ZIP.`,
      }
    }
    // Vérification de la taille (200 Mo max)
    const MAX_SIZE = 200 * 1024 * 1024 // 200 Mo en octets
    if (file.size > MAX_SIZE) {
      return {
        valid: false,
        message: `Fichier trop volumineux: ${(file.size / (1024 * 1024)).toFixed(2)} Mo. Maximum: 200 Mo.`,
      }
    }
    return { valid: true }
  }

  async function sendFileAndPoll (formData: FormData) {
    // Récupérer le fichier pour validation
    const file = formData.get('file') as File
    if (file) {
      const validation = validateFile(file)
      if (!validation.valid) {
        error.value = validation.message
        return
      }
      originalFileName.value = file.name
    }

    processingState.value = 'uploading'
    const ok = await healthCheck()
    if (!ok) {
      processingState.value = 'idle'
      return
    }

    try {
      const { data: task } = await http.post<TaskModel>(`/jobs/`, formData)

      if (!task?.id) {
        throw new Error('Réponse API invalide: ID de tâche manquant')
      }

      await pollTask(task.id)
    } catch (err: any) {
      // Extraire le message d'erreur le plus pertinent
      let errorMessage = 'Erreur lors de l\'envoi du fichier.'
      if (err.response) {
        // Erreur de l'API avec réponse
        const status = err.response.status
        switch (status) {
          case 413:
            errorMessage = 'Fichier trop volumineux pour le serveur'
            break
          case 415:
            errorMessage = 'Type de fichier non supporté'
            break
          default:
            errorMessage = err.response.data.message
            break
        }
      } else if (err.message) {
        errorMessage = err.message
      }
      error.value = errorMessage
      isPolling.value = false
      processingState.value = 'idle'
    }
  }

  /**
   * Stops an in-flight `pollTask` loop. Safe to call when nothing is polling.
   */
  function stopPolling () {
    isPolling.value = false
    if (processingState.value === 'processing') {
      processingState.value = 'idle'
    }
  }

  function reset () {
    status.value = null
    percentage.value = 0
    taskData.value = null
    isPolling.value = false
    error.value = undefined
    processingState.value = 'idle'
  }

  /**
   * Télécharge le texte OCR pour un taskId donné.
   * Crée un fichier .txt et déclenche le téléchargement côté client.
   */
  async function downloadText (taskId: string): Promise<void> {
    try {
      const response = await http.get<string>(
        `/text-task/${taskId}`,
        {
          headers: { accept: 'text/plain' },
        },
      )

      const text = response.data
      const blob = new Blob([text], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)

      const a = document.createElement('a')
      a.href = url

      const baseName = originalFileName.value
        ? originalFileName.value.replace(/\.[^/.]+$/, '')
        : `ocr-output-${taskId}`
      a.download = `${baseName}.txt`

      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)

      URL.revokeObjectURL(url)
    } catch (error) {
      addErrorMessage({
        title: 'Erreur :',
        description: `Erreur lors du téléchargement du texte OCR : ${error}`,
      })
      throw error
    }
  }

  return {
    status,
    percentage,
    taskData,
    isPolling,
    error,
    position,

    getTask,
    getPageImageUrl,
    sendFileAndPoll,
    pollTask,
    stopPolling,
    reset,
    validateFile,
    downloadText,
  }
})
