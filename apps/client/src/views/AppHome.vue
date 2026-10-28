<script setup lang="ts">
import DocumentDownload from '@gouvfr/dsfr/dist/artwork/pictograms/document/document-download.svg'
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Media from '@/assets/ocr-card.svg'
import ComminitySVG from '@/assets/pictograms/community.svg'
import PenSVG from '@/assets/pictograms/pen.svg'
import CustomCard from '@/components/CustomCard.vue'
import CustomTabs from '@/components/CustomTabs.vue'
import InfoBulle from '@/components/InfoBulle.vue'
import OcrViewer from '@/components/OcrViewer.vue'
import ProgressBar from '@/components/ProgressBar.vue'
import SideBar from '@/components/SideBar.vue'
import TasksTab from '@/components/TasksTab.vue'
import { useOcrStore } from '@/stores/ocr'

const route = useRoute()
const router = useRouter()
const store = useOcrStore()
const selectedFile = ref<File | null>(null)
const pdfUrl = ref<string | null>(null)
const uploadError = computed(() => store.error)
const progressPercent = computed(() => Math.round(store.percentage * 100))
const isPolling = computed(() => store.isPolling)
const taskData = computed(() => store.taskData)
const status = computed(() => store.status)
const isLoading = ref(false)

function selectFile (files: FileList | File[]) {
  const file = Array.isArray(files)
    ? files[0]
    : files[0] || null
  if (file) {
    pdfUrl.value = URL.createObjectURL(file)
    selectedFile.value = file
    store.reset()
  }
}

async function startOcr () {
  if (!selectedFile.value) {
    return
  }

  isLoading.value = true

  try {
    const form = new FormData()
    form.append('file', selectedFile.value)
    await store.sendFileAndPoll(form)
  } finally {
    isLoading.value = false
  }
}

const myOtherTools = ref([
  {
    title: 'Converser avec le Chatbot',
    to: '/outils-mirai/chat',
    imgSrc: ComminitySVG,
  },
  {
    title: 'Résumer un texte',
    to: '/outils-mirai/resume',
    imgSrc: PenSVG,
  },
  {
    title: 'Faire un compte rendu',
    to: '/outils-mirai/compte-rendu',
    imgSrc: DocumentDownload,
  },
])

const uploadHint = `Taille maximale : 200 Mo. Formats supportés : jpg, png, pdf, docx, xlsx, odt, ods, odp, csv, eml, zip. Plus la qualité du fichier sera élevée, plus l'outil de reconnaissance de texte sera performant.`
const uploadLabel = 'Ajouter un fichier'
const uploadAccept = [
  'image/jpeg',
  'image/png',
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // docx
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // xlsx
  'application/vnd.oasis.opendocument.text', // odt
  'application/vnd.oasis.opendocument.spreadsheet', // ods
  'application/vnd.oasis.opendocument.presentation', // odp
  'text/csv',
  'message/rfc822', // eml
  'application/zip', // zip
  'application/x-zip-compressed', // zip
].join(',')

const tabs = ref([
  { label: 'OCR', slot: 'tab-0-content' },
  { label: 'Mes tâches', slot: 'tab-1-content' },
])

// Seul OCR a une route dédiée ; "Mes tâches" reste un onglet local
// (pas de navigation) pour rester sur la page courante.
const routeForTabIndex: Record<number, string> = { 0: '/ocr' }

const activeTabIndex = ref(0)

watch(() => route.path, (path) => {
  if (path === '/ocr') { activeTabIndex.value = 0 }
})

watch(activeTabIndex, (index) => {
  const target = routeForTabIndex[index]
  if (target && target !== route.path) { router.push(target) }
})

const cardTitle = `Comment utiliser “Extraire un texte” ?`
const cardInfos = `
  <ol>
    <li>Ajoutez un PDF avec un texte scanné (texte numérisé, photo d’un texte imprimé, formulaire, ...)</li>
    <li>Cliquez sur “Extraire le texte”</li>
  </ol>
  <p>Les textes scannés apparaissent en rouge. Vous pouvez extraire et télécharger le contenu du fichier en fichier .txt.</p>
`
const cardHint = `💡 Les textes scannés apparaissent en rouge. Vous pouvez extraire et télécharger le contenu du fichier en fichier .txt.`

onBeforeUnmount(() => {
  if (pdfUrl.value) {
    URL.revokeObjectURL(pdfUrl.value)
  }
})
</script>

<template>
  <div class="main-page">
    <SideBar :other-tools="myOtherTools" />
    <div class="main-page__container">
      <div class="mt-[35px]">
        <h1 class="flex items-center gap-3">
          <span>Reconnaître un texte scanné </span>
        </h1>
      </div>

      <CustomTabs
        v-model="activeTabIndex"
        :tabs-data="tabs"
      >
        <template #tab-0-content>
          <InfoBulle />
          <div class="page-container">
            <div class="file-upload-container flex flex-col">
              <DsfrFileUpload
                :label="uploadLabel"
                :hint="uploadHint"
                :error="uploadError"
                :accept="uploadAccept"
                @change="selectFile"
              />

              <div class="mt-4">
                <DsfrButton
                  label="Extraire le texte"
                  size="lg"
                  :disabled="!selectedFile || isPolling || isLoading"
                  @click="startOcr"
                />
              </div>

              <ProgressBar
                :visible="isPolling && status === 'in_progress'"
                :progress="progressPercent"
              />

              <div class="flex justify-center">
                <OcrViewer
                  v-if="taskData?.output && !isPolling"
                  :data="{ id: taskData.id, pages: taskData.output.pages }"
                />
              </div>
            </div>
          </div>
        </template>

        <template #tab-1-content>
          <TasksTab :is-active="activeTabIndex === 1" />
        </template>
      </CustomTabs>

      <CustomCard
        :img-src="Media"
        img-alt="image de stylo sur feuille de papier"
        :title="cardTitle"
        description=""
        :infos="cardInfos"
        :hint="cardHint"
      />
    </div>
  </div>
</template>
