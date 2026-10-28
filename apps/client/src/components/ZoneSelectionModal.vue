<script setup lang="ts">
import { computed } from 'vue'
import useToaster from '@/composables/use-toaster'

interface Selection {
  x: number
  y: number
  w: number
  h: number
}

const props = defineProps<{
  show: boolean
  imageUrl: string | undefined
  text: string
  selection: Selection
  imgWidth: number
  imgHeight: number
}>()

const emit = defineEmits<{
  close: []
}>()

const { addSuccessMessage, addErrorMessage } = useToaster()

// CSS-based crop — no canvas, no CORS issue
// Aspect ratio du wrapper = dimensions en pixels de la sélection
const wrapperStyle = computed(() => {
  const { w, h } = props.selection
  const W = props.imgWidth || 1
  const H = props.imgHeight || 1
  return {
    width: '100%',
    // ratio réel en pixels : largeur_sélection / hauteur_sélection
    aspectRatio: `${w * W} / ${h * H}`,
    overflow: 'hidden',
    position: 'relative' as const,
    backgroundColor: '#f0f0f0',
  }
})

const imgStyle = computed(() => {
  const { x, y, w, h } = props.selection
  // Échelle : image affichée à 100%/sel.w de la largeur du container
  // → la portion sel.w remplit exactement le container
  // left/top en % du container (left → % width, top → % height)
  return {
    position: 'absolute' as const,
    width: `${(1 / (w || 0.001)) * 100}%`,
    height: 'auto', // ratio naturel maintenu automatiquement
    left: `-${(x / (w || 0.001)) * 100}%`, // % de la largeur du container
    top: `-${(y / (h || 0.001)) * 100}%`, // % de la hauteur du container
    maxWidth: 'none',
    display: 'block',
  }
})

function copyText () {
  navigator.clipboard.writeText(props.text)
    .then(() => addSuccessMessage({
      title: 'Copié',
      description: props.text.slice(0, 100),
    }))
    .catch(err => addErrorMessage({
      title: 'Erreur copie',
      description: String(err),
    }))
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 z-[9999] flex items-center justify-center"
      @click.self="emit('close')"
    >
      <div class="bg-white w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded shadow-xl p-6">
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <h2 class="fr-h5 mb-0">
            Zone sélectionnée
          </h2>
          <button
            class="fr-btn fr-btn--tertiary-no-outline fr-btn--sm fr-btn--icon-only"
            title="Fermer"
            @click="emit('close')"
          >
            <span
              class="fr-icon-close-line"
              aria-hidden="true"
            />
          </button>
        </div>

        <!-- Aperçu CSS crop (sans canvas, sans CORS) -->
        <div
          v-if="imageUrl"
          :style="wrapperStyle"
          class="mb-4 border border-gray-200"
        >
          <img
            :src="imageUrl"
            alt="Zone sélectionnée"
            :style="imgStyle"
          >
        </div>
        <div
          v-else
          class="text-sm text-gray-400 italic mb-4"
        >
          (aperçu non disponible)
        </div>

        <!-- Texte extrait -->
        <div class="mb-4">
          <p class="text-sm font-semibold mb-1 text-gray-600">
            Texte extrait :
          </p>
          <div class="bg-gray-50 border border-gray-200 rounded p-3 text-sm whitespace-pre-wrap min-h-[3rem]">
            {{ text || '(aucun texte dans cette zone)' }}
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-2 justify-end">
          <DsfrButton
            label="Copier le texte"
            icon="fr-icon-clipboard-line"
            secondary
            :disabled="!text"
            @click="copyText"
          />
          <DsfrButton
            label="Fermer"
            @click="emit('close')"
          />
        </div>
      </div>
    </div>
  </Teleport>
</template>
