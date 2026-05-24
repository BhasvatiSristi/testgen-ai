<template>
  <section class="surface-card config-panel">
    <div class="section-heading">
      <div>
        <p class="eyebrow">Configuration</p>
        <h2>Shape the output</h2>
      </div>
      <span class="soft-chip">{{ depthLabel }} depth</span>
    </div>

    <div class="field-group">
      <label class="field-label" for="framework">Framework</label>
      <div class="framework-switch" role="group" aria-label="Framework options">
        <button
          v-for="option in frameworkOptions"
          :key="option"
          type="button"
          class="framework-option"
          :class="{ active: framework === option }"
          @click="selectFramework(option)"
        >
          {{ option }}
        </button>
      </div>
    </div>

    <div class="field-group">
      <label class="field-label">Test types</label>
      <div class="chip-grid">
        <button
          v-for="type in testTypeOptions"
          :key="type"
          class="toggle-chip"
          :class="{ active: testTypes.includes(type) }"
          type="button"
          @click="toggleTestType(type)"
        >
          {{ type }}
        </button>
      </div>
    </div>

    <div class="field-group">
      <label class="field-label">Coverage depth</label>
      <div class="depth-switch">
        <button
          v-for="option in depthOptions"
          :key="option.value"
          :class="['depth-option', { active: option.value === coverageDepth }]"
          type="button"
          @click="$emit('update:coverageDepth', option.value)"
        >
          <strong>{{ option.label }}</strong>
          <span>{{ option.helper }}</span>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  framework: {
    type: String,
    default: 'pytest',
  },
  testTypes: {
    type: Array,
    default: () => ['Unit tests', 'Integration tests', 'Edge cases'],
  },
  coverageDepth: {
    type: Number,
    default: 2,
  },
})

const emit = defineEmits(['update:framework', 'update:testTypes', 'update:coverageDepth'])

const frameworkOptions = ['pytest', 'jest', 'junit', 'rspec']
const testTypeOptions = ['Unit tests', 'Integration tests', 'Edge cases', 'Mocks/Fixtures']
const depthOptions = [
  { value: 1, label: 'Basic', helper: 'fast and focused' },
  { value: 2, label: 'Medium', helper: 'balanced coverage' },
  { value: 3, label: 'Deep', helper: 'broader edge sweep' },
]

const depthLabel = computed(() => depthOptions.find((option) => option.value === props.coverageDepth)?.label || 'Medium')

function selectFramework(option) {
  emit('update:framework', option)
}

function toggleTestType(type) {
  const nextTypes = props.testTypes.includes(type)
    ? props.testTypes.filter((item) => item !== type)
    : [...props.testTypes, type]

  emit('update:testTypes', nextTypes)
}
</script>
