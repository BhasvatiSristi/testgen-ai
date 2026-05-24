<template>
  <section class="surface-card output-workspace">
    <div class="section-heading">
      <div>
        <p class="eyebrow">Generated tests</p>
        <h2>Preview and copy</h2>
      </div>
      <div class="inline-actions">
        <button class="ghost-button" type="button" @click="copyAll">Copy all</button>
      </div>
    </div>

    <div class="tab-strip">
      <button
        v-for="section in sections"
        :key="section.key"
        type="button"
        class="tab-button"
        :class="{ active: activeSection === section.key }"
        @click="activeSection = section.key"
      >
        {{ section.label }}
      </button>
    </div>

    <div class="preview-shell">
      <div class="preview-header">
        <span class="soft-chip">{{ activeSectionLabel }}</span>
        <div class="inline-actions">
          <button class="ghost-button" type="button" @click="downloadActive">Download</button>
        </div>
      </div>
      <pre class="code-preview"><code>{{ currentContent || 'Generate tests to see the output here.' }}</code></pre>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'

import { copyText, downloadText } from '../lib/download'

const props = defineProps({
  generatedTests: {
    type: Object,
    default: () => ({ unit: '', integration: '', edge_cases: '' }),
  },
  framework: {
    type: String,
    default: 'pytest',
  },
})

const sections = [
  { key: 'unit', label: 'Unit tests' },
  { key: 'integration', label: 'Integration' },
  { key: 'edge_cases', label: 'Edge cases' },
]

const activeSection = ref('unit')

const activeSectionLabel = computed(() => sections.find((section) => section.key === activeSection.value)?.label || 'Unit tests')
const currentContent = computed(() => props.generatedTests[activeSection.value] || '')

function fileNameForSection(sectionKey) {
  const extension = {
    pytest: 'py',
    jest: 'js',
    junit: 'java',
    rspec: 'rb',
  }[props.framework] || 'txt'

  return {
    unit: `unit_tests.${extension}`,
    integration: `integration_tests.${extension}`,
    edge_cases: `edge_case_tests.${extension}`,
  }[sectionKey]
}

function downloadActive() {
  downloadText(fileNameForSection(activeSection.value), currentContent.value)
}

async function copyAll() {
  const combined = sections
    .map((section) => `# ${section.label}\n${props.generatedTests[section.key] || ''}`)
    .join('\n\n')

  await copyText(combined)
}
</script>
