<template>
  <section class="surface-card export-panel">
    <div class="section-heading">
      <div>
        <p class="eyebrow">Export</p>
        <h2>Download or push to GitHub</h2>
      </div>
      <button class="ghost-button" type="button" @click="copyAll">Copy all tests</button>
    </div>

    <div class="download-row">
      <button class="ghost-button" type="button" @click="download('unit')">Download unit</button>
      <button class="ghost-button" type="button" @click="download('integration')">Download integration</button>
      <button class="ghost-button" type="button" @click="download('edge_cases')">Download edge cases</button>
    </div>

    <div class="export-form">
      <div class="field-group">
        <label class="field-label" for="github-repo">GitHub repo</label>
        <input id="github-repo" :value="repo" placeholder="owner/repo" @input="$emit('update:repo', $event.target.value)" />
      </div>

      <div class="field-group">
        <label class="field-label" for="github-token">GitHub token</label>
        <input id="github-token" :value="token" type="password" placeholder="Personal access token" @input="$emit('update:token', $event.target.value)" />
      </div>

      <button class="primary-button" type="button" :disabled="exporting" @click="$emit('export-github')">
        {{ exporting ? 'Pushing...' : 'Push to GitHub' }}
      </button>
    </div>
  </section>
</template>

<script setup>
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
  repo: {
    type: String,
    default: '',
  },
  token: {
    type: String,
    default: '',
  },
  exporting: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:repo', 'update:token', 'export-github'])

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

function download(sectionKey) {
  downloadText(fileNameForSection(sectionKey), props.generatedTests[sectionKey] || '')
}

async function copyAll() {
  const combined = [
    '# Unit tests\n' + (props.generatedTests.unit || ''),
    '# Integration tests\n' + (props.generatedTests.integration || ''),
    '# Edge case tests\n' + (props.generatedTests.edge_cases || ''),
  ].join('\n\n')

  await copyText(combined)
}
</script>
