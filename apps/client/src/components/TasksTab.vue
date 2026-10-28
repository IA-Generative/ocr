<script setup lang="ts">
import type { components } from '@/api/types/api.schema'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import createHttpClient from '@/api/http-client'
import { useTasksStore } from '@/stores/tasks'
import { OCR_API_URL } from '@/utils/constants'
import ProgressBar from './ProgressBar.vue'

type TaskModel = components['schemas']['TaskModel']
type SortableTaskKey = 'type' | 'percentage' | 'created_at' | 'updated_at'

const props = defineProps<{
  /** Whether this tab is the one currently visible (e.g. `activeTabIndex === 1` in
   * the parent) - `CustomTabs` keeps every tab mounted (`v-show`, not `v-if`), so
   * without this the list only ever loads once and goes stale as soon as the user
   * switches away and back. */
  isActive?: boolean
}>()

const store = useTasksStore()
const router = useRouter()
const http = createHttpClient(OCR_API_URL)

const PAGE_SIZE = 20

// DsfrPagination's `current-page` is 0-indexed; the API's `page` query param is 1-indexed.
const currentPage = ref(0)

const totalPages = computed(() => {
  const total = store.userTasksPaginated?.total ?? 0
  return total > 0
    ? Math.ceil(total / PAGE_SIZE)
    : 0
})

const paginationPages = computed(() =>
  Array.from({ length: totalPages.value }, (_, idx) => ({
    href: '#',
    label: String(idx + 1),
    title: `Page ${idx + 1}`,
  })),
)

// ----- TRI -----
const sortKey = ref<SortableTaskKey>('created_at')
const sortAsc = ref(false)

const sortOptions: { key: SortableTaskKey, label: string }[] = [
  { key: 'type', label: 'Type' },
  { key: 'percentage', label: 'Pourcentage' },
  { key: 'created_at', label: 'Créé le' },
  { key: 'updated_at', label: 'Mis à jour le' },
]

function goToDetail (taskId: string) {
  router.push(`/tasks/${taskId}`)
}

function MapStatusToLabel (status: string) {
  const map: Record<string, string> = {
    queued: 'En attente',
    in_progress: 'En cours',
    completed: 'Terminé',
    failed: 'Échoué',
  }
  return map[status] || status
}

function sortBy (key: SortableTaskKey) {
  if (sortKey.value === key) {
    sortAsc.value = !sortAsc.value
  } else {
    sortKey.value = key
    sortAsc.value = true
  }
}

const sortedTasks = computed(() => {
  const items: TaskModel[] = store.userTasksPaginated?.items ?? []
  if (!sortKey.value) {
    return items
  }
  return [...items].sort((a, b) => {
    // `percentage` can be null (task not yet processed); treat it as 0 for sorting.
    const valA = a[sortKey.value] ?? 0
    const valB = b[sortKey.value] ?? 0
    if (valA === valB) {
      return 0
    }
    if (sortAsc.value) {
      return valA > valB
        ? 1
        : -1
    }
    return valA < valB
      ? 1
      : -1
  })
})

async function loadPage (page: number) {
  await store.fetchUserTasks(page + 1, PAGE_SIZE)
}

watch(currentPage, (page) => {
  void loadPage(page)
})

// Reload whenever the tab becomes the visible one, so switching back to it after
// creating/finishing a task shows current data instead of whatever was last fetched.
watch(() => props.isActive, (active) => {
  if (active) {
    void loadPage(currentPage.value)
  }
})

onMounted(() => {
  void loadPage(currentPage.value)
})

onBeforeUnmount(() => {
  if (typeof store.stopPollingUserTasks === 'function') {
    store.stopPollingUserTasks()
  }
})

// ----- TÉLÉCHARGEMENT -----
async function downloadTaskResult (task: TaskModel) {
  if (!task || task.status !== 'completed') {
    return
  }
  try {
    const { data: text } = await http.get<string>(`/text-task/${encodeURIComponent(task.id)}`, {
      headers: { accept: 'text/plain' },
    })
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const baseName = task.input?.raw_filename
      ? task.input.raw_filename.replace(/\.[^/.]+$/, '')
      : `ocr-output-${task.id}`
    a.download = `${baseName}.txt`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Téléchargement échoué', e)
  }
}

// ----- SUPPRESSION -----
async function removeTask (taskId: string) {
  if (!taskId) {
    return
  }
  try {
    await store.deleteTask(taskId)
  } catch {
    // store already shows error toast
  }
}

function formatDate (ts: number | null | undefined) {
  if (ts === null || ts === undefined) {
    return ''
  }
  try {
    let n = Number(ts)
    if (Number.isNaN(n)) {
      return String(ts)
    }
    if (n < 1e12) {
      n = n * 1000
    }
    return new Date(n).toLocaleString()
  } catch {
    return String(ts)
  }
}
</script>

<template>
  <div class="task-container fr-container">
    <div class="task-header">
      <h2 class="fr-h2 task-header-title">
        Liste des tâches
        <span
          v-if="store.userTasksPaginated?.total"
          class="fr-text--sm task-total"
        >
          ({{ store.userTasksPaginated.total }} au total)
        </span>
      </h2>

      <DsfrButton
        size="sm"
        priority="secondary"
        icon="fr-icon-refresh-line"
        :icon-only="false"
        :disabled="store.loading"
        :label="store.loading ? 'Mise à jour…' : 'Mettre à jour'"
        @click="loadPage(currentPage)"
      />
    </div>

    <div class="task-sort-bar">
      <span class="fr-text--sm task-sort-label">Trier par :</span>
      <DsfrButton
        v-for="option in sortOptions"
        :key="option.key"
        size="sm"
        :priority="sortKey === option.key ? 'primary' : 'tertiary'"
        @click="sortBy(option.key)"
      >
        {{ option.label }}<span v-if="sortKey === option.key">{{ sortAsc ? ' ↑' : ' ↓' }}</span>
      </DsfrButton>
    </div>

    <div class="task-tile-grid">
      <div
        v-for="task in sortedTasks"
        :key="task.id"
        class="task-tile"
      >
        <div class="task-tile-title">
          <span v-if="task.input?.raw_filename">{{ task.input.raw_filename }}</span>
          <span v-else>Inconnu</span>
        </div>

        <ProgressBar
          :visible="true"
          :progress="(task.percentage ?? 0) * 100"
          :text="MapStatusToLabel(task.status)"
        />

        <dl class="task-tile-dates">
          <div>
            <dt>Créé le</dt>
            <dd>{{ formatDate(task.created_at) }}</dd>
          </div>
          <div>
            <dt>Mis à jour le</dt>
            <dd>{{ formatDate(task.updated_at) }}</dd>
          </div>
        </dl>

        <div class="task-tile-actions">
          <DsfrButton
            size="sm"
            priority="tertiary"
            @click="goToDetail(task.id)"
          >
            Voir le détail
          </DsfrButton>

          <DsfrButton
            size="sm"
            priority="secondary"
            :disabled="task.status !== 'completed'"
            @click="downloadTaskResult(task)"
          >
            Voir résultat
          </DsfrButton>

          <DsfrButton
            size="sm"
            priority="tertiary"
            @click="removeTask(task.id)"
          >
            Supprimer
          </DsfrButton>
        </div>
      </div>
    </div>

    <div
      v-if="totalPages > 1"
      class="task-pagination"
    >
      <DsfrPagination
        v-model:current-page="currentPage"
        :pages="paginationPages"
        :trunc-limit="5"
      />
    </div>
  </div>
</template>

<style scoped>
.task-container {
  padding: 20px;
}

.task-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.task-header-title {
  margin-bottom: 0;
}

.task-sort-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.task-sort-label {
  margin-right: 0.25rem;
}

.task-total {
  font-weight: normal;
  color: #666;
}

.task-pagination {
  display: flex;
  justify-content: center;
  margin-top: 1.5rem;
}

.task-tile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.task-tile {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  background: #fff;
}

.task-tile-title {
  font-weight: bold;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.task-tile-dates {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 1.5rem;
  margin: 0;
  font-size: 0.875rem;
}

.task-tile-dates dt {
  color: #666;
}

.task-tile-dates dd {
  margin: 0;
}

.task-tile-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: auto;
}
</style>
