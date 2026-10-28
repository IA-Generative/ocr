<script setup lang="ts">
import type { CSSProperties } from 'vue'
import type { components } from '@/api/types/api.schema'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import ZoneSelectionModal from '@/components/ZoneSelectionModal.vue'
import useToaster from '@/composables/use-toaster'
import { useOcrStore } from '@/stores/ocr'

type Bbox = components['schemas']['Bbox']
type Page = components['schemas']['Page']

interface PaginationPage {
  href?: string
  label: string
  title: string
}
interface SearchResult {
  pageIdx: number
  boxIdx: number
  text: string
}

const props = defineProps<{ data: { id?: string, pages: Page[] } }>()

const store = useOcrStore()
const { addErrorMessage, addSuccessMessage } = useToaster()
const pages = props.data.pages
const currentPage = ref(0)

const paginationPages = computed<PaginationPage[]>(() =>
  pages.map((_, idx) => ({
    href: '#',
    label: String(idx + 1),
    title: `Page ${idx + 1}`,
  })),
)

const imageUrl = ref<string | undefined>(undefined)

function revokeCurrentImageUrl () {
  if (imageUrl.value) { URL.revokeObjectURL(imageUrl.value) }
}

async function loadCurrentPageImage () {
  const taskId = props.data.id
  const page = pages[currentPage.value]
  if (!taskId || !page?.page_url) {
    revokeCurrentImageUrl()
    imageUrl.value = undefined
    return
  }
  try {
    const url = await store.getPageImageUrl(taskId, currentPage.value + 1)
    revokeCurrentImageUrl()
    imageUrl.value = url
  } catch (err) {
    imageUrl.value = undefined
    addErrorMessage({ title: 'Erreur', description: `Impossible de charger l'image de la page : ${err}` })
  }
}

watch(currentPage, loadCurrentPageImage, { immediate: true })
onBeforeUnmount(revokeCurrentImageUrl)
const boxes = computed<Bbox[]>(() => pages[currentPage.value]?.boxes || [])
const showImage = ref(true)

// Feature 3 : bboxes affichees par defaut
const showBboxes = ref(true)

// Feature 1 : recherche
const searchQuery = ref('')
const showSearchResults = ref(false)

const searchResults = computed<SearchResult[]>(() => {
  const q = searchQuery.value.toLowerCase().trim()
  if (!q) { return [] }
  const results: SearchResult[] = []
  pages.forEach((page, pageIdx) => {
    page.boxes?.forEach((box, boxIdx) => {
      if (box.text.toLowerCase().includes(q)) { results.push({ pageIdx, boxIdx, text: box.text }) }
    })
  })
  return results
})

const matchingBoxIndices = computed<Set<number>>(() => {
  if (!searchQuery.value.trim()) { return new Set() }
  return new Set(
    searchResults.value.filter(r => r.pageIdx === currentPage.value).map(r => r.boxIdx),
  )
})

function goToResult (result: SearchResult) {
  currentPage.value = result.pageIdx
  showSearchResults.value = false
}

// Feature 2 : selection de zone
const containerRef = ref<HTMLDivElement | null>(null)
const imgRef = ref<HTMLImageElement | null>(null)
const imgDimensions = ref({ width: 0, height: 0 })
const isSelectMode = ref(false)
const isSelecting = ref(false)
const selStart = ref({ x: 0, y: 0 })
const selEnd = ref({ x: 0, y: 0 })
const showZoneModal = ref(false)
const zoneText = ref('')
const savedSel = ref({ x: 0, y: 0, w: 0.1, h: 0.1 })

const normalizedSel = computed(() => {
  const x1 = Math.min(selStart.value.x, selEnd.value.x)
  const y1 = Math.min(selStart.value.y, selEnd.value.y)
  const x2 = Math.max(selStart.value.x, selEnd.value.x)
  const y2 = Math.max(selStart.value.y, selEnd.value.y)
  return { x: x1, y: y1, w: x2 - x1, h: y2 - y1 }
})

const selectionStyle = computed<CSSProperties>(() => {
  const { x, y, w, h } = normalizedSel.value
  const W = imgDimensions.value.width
  const H = imgDimensions.value.height
  return {
    position: 'absolute',
    left: `${x * W}px`,
    top: `${y * H}px`,
    width: `${w * W}px`,
    height: `${h * H}px`,
    border: '2px dashed #0063CB',
    backgroundColor: 'rgba(0,99,203,0.10)',
    pointerEvents: 'none',
    zIndex: 30,
  }
})

function getRelativeCoords (e: MouseEvent) {
  if (!containerRef.value) { return { x: 0, y: 0 } }
  const rect = containerRef.value.getBoundingClientRect()
  const W = imgDimensions.value.width || 1
  const H = imgDimensions.value.height || 1
  return {
    x: Math.max(0, Math.min(1, (e.clientX - rect.left) / W)),
    y: Math.max(0, Math.min(1, (e.clientY - rect.top) / H)),
  }
}

function onMouseDown (e: MouseEvent) {
  if (!isSelectMode.value) { return }
  isSelecting.value = true
  const c = getRelativeCoords(e)
  selStart.value = c
  selEnd.value = c
}
function onGlobalMouseMove (e: MouseEvent) {
  if (!isSelecting.value) { return }
  selEnd.value = getRelativeCoords(e)
}
function onGlobalMouseUp () {
  if (!isSelecting.value) { return }
  isSelecting.value = false
  const sel = normalizedSel.value
  if (sel.w < 0.005 || sel.h < 0.005) { return }
  const boxesInZone = boxes.value.filter(box =>
    box.x < sel.x + sel.w && box.x + box.width > sel.x
    && box.y < sel.y + sel.h && box.y + box.height > sel.y,
  )
  zoneText.value = boxesInZone.map(b => b.text).join(' ')
  savedSel.value = { ...sel }
  showZoneModal.value = true
}

let resizeObserver: ResizeObserver
onMounted(() => {
  if (!imgRef.value) { return }
  imgDimensions.value = { width: imgRef.value.clientWidth, height: imgRef.value.clientHeight }
  resizeObserver = new ResizeObserver((entries) => {
    for (const { contentRect } of entries) { imgDimensions.value = { width: contentRect.width, height: contentRect.height } }
  })
  resizeObserver.observe(imgRef.value)
  // Listeners globaux pour capturer mouseup même hors du container
  window.addEventListener('mousemove', onGlobalMouseMove)
  window.addEventListener('mouseup', onGlobalMouseUp)
})
onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  window.removeEventListener('mousemove', onGlobalMouseMove)
  window.removeEventListener('mouseup', onGlobalMouseUp)
})

function styleForBox (box: Bbox, isMatch: boolean): CSSProperties {
  const W = imgDimensions.value.width
  const H = imgDimensions.value.height
  return {
    position: 'absolute',
    left: `${box.x * W}px`,
    top: `${box.y * H}px`,
    width: `${box.width * W}px`,
    height: `${box.height * H}px`,
    zIndex: 20,
    backgroundColor: isMatch ? 'rgba(255,200,0,0.4)' : 'rgba(255,0,0,0.2)',
    border: `1px solid ${isMatch ? 'rgba(200,150,0,0.9)' : 'rgba(255,0,0,0.6)'}`,
  }
}

function copyText (text: string) {
  navigator.clipboard.writeText(text)
    .then(() => addSuccessMessage({ title: 'Copie', description: text }))
    .catch(err => addErrorMessage({
      title: 'Erreur copie',
      description: String(err),
    }))
}

async function onDownloadText () {
  if (!props.data.id) { return }
  try {
    await store.downloadText(props.data.id)
    addSuccessMessage({ title: 'Succes', description: 'Document telecharge.' })
  } catch (error) {
    addErrorMessage({
      title: 'Erreur',
      description: String(error),
    })
  }
}
</script>

<template>
  <div class="w-full max-w-4xl mx-auto">
    <!-- Barre d'outils -->
    <div class="my-4 flex flex-wrap gap-2 items-center">
      <DsfrButton
        size="sm"
        :label="showImage ? 'Masquer image' : 'Afficher image'"
        secondary
        class="hidden md:inline-flex"
        @click="showImage = !showImage"
      />
      <!-- Feature 3 : toggle bboxes -->
      <DsfrButton
        size="sm"
        :icon="showBboxes ? 'fr-icon-eye-off-line' : 'fr-icon-eye-line'"
        :label="showBboxes ? 'Masquer zones' : 'Afficher zones'"
        secondary
        class="hidden md:inline-flex"
        @click="showBboxes = !showBboxes"
      />
      <!-- Feature 2 : mode selection -->
      <DsfrButton
        size="sm"
        icon="fr-icon-crop-line"
        :label="isSelectMode ? 'Annuler selection' : 'Selectionner zone'"
        :secondary="!isSelectMode"
        class="hidden md:inline-flex"
        @click="isSelectMode = !isSelectMode"
      />
      <DsfrButton
        size="sm"
        label="Telecharger"
        secondary
        @click="onDownloadText"
      />
    </div>

    <!-- Feature 1 : recherche -->
    <div class="relative mb-4">
      <DsfrSearchBar
        v-model="searchQuery"
        label="Rechercher dans le texte"
        placeholder="Mot, phrase..."
        :show-label="false"
        @input="showSearchResults = true"
      />
      <div
        v-if="showSearchResults && searchQuery.trim() && searchResults.length"
        class="absolute z-50 w-full bg-white border border-gray-200 shadow-lg max-h-60 overflow-y-auto"
      >
        <div
          v-for="(result, i) in searchResults"
          :key="i"
          class="px-3 py-2 hover:bg-blue-50 cursor-pointer flex items-start gap-2 border-b last:border-b-0"
          @click="goToResult(result)"
        >
          <span class="fr-badge fr-badge--sm fr-badge--info shrink-0">p.{{ result.pageIdx + 1 }}</span>
          <span class="text-sm truncate">{{ result.text }}</span>
        </div>
      </div>
      <div
        v-if="showSearchResults && searchQuery.trim() && !searchResults.length"
        class="absolute z-50 w-full bg-white border border-gray-200 shadow px-3 py-2 text-sm text-gray-500"
      >
        Aucun resultat
      </div>
      <div
        v-if="searchResults.length && searchQuery.trim()"
        class="mt-1 text-xs text-gray-500"
      >
        {{ searchResults.length }} resultat{{ searchResults.length > 1 ? 's' : '' }} — {{ new Set(searchResults.map(r => r.pageIdx)).size }} page{{ new Set(searchResults.map(r => r.pageIdx)).size > 1 ? 's' : '' }}
      </div>
    </div>

    <!-- Image + bboxes -->
    <div
      ref="containerRef"
      class="relative w-full border border-slate-300 hidden md:block"
      :class="isSelectMode ? 'cursor-crosshair' : ''"
      @mousedown="onMouseDown"
    >
      <img
        ref="imgRef"
        :src="imageUrl"
        alt="OCR page"
        class="block w-full h-auto select-none transition-opacity duration-300"
        :class="showImage ? 'opacity-100' : 'opacity-0'"
        draggable="false"
      >

      <!-- Feature 3 : bboxes conditionnelles -->
      <template v-if="showBboxes || matchingBoxIndices.size > 0">
        <div
          v-for="(box, idx) in boxes"
          :key="idx"
          :style="styleForBox(box, matchingBoxIndices.has(idx))"
          :class="(showBboxes || matchingBoxIndices.has(idx)) ? 'pointer-events-auto' : 'pointer-events-none opacity-0'"
        >
          <button
            class="absolute top-[-10px] left-[-25px] z-30"
            @click.stop="copyText(box.text)"
          >
            <span
              class="fr-icon-draft-line"
              aria-hidden="true"
            />
          </button>
        </div>
      </template>

      <!-- Rectangle selection en cours -->
      <div
        v-if="isSelecting && normalizedSel.w > 0"
        :style="selectionStyle"
      />
    </div>

    <div class="my-4">
      <DsfrAlert>
        L'extraction peut comporter des erreurs, veuillez verifier les resultats.
      </DsfrAlert>
    </div>

    <div class="mt-4 hidden md:flex justify-center">
      <DsfrPagination
        v-model:current-page="currentPage"
        :pages="paginationPages"
        :trunc-limit="5"
      />
    </div>

    <!-- Feature 2 : modal zone selectionnee (composant separe) -->
    <ZoneSelectionModal
      :show="showZoneModal"
      :image-url="imageUrl"
      :text="zoneText"
      :selection="savedSel"
      :img-width="imgDimensions.width"
      :img-height="imgDimensions.height"
      @close="showZoneModal = false"
    />
  </div>
</template>

<style scoped>
.cursor-crosshair { cursor: crosshair; }
</style>
