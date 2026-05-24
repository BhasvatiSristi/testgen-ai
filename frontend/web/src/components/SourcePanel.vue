<template>
  <section class="surface-card source-panel">
    <div class="section-heading">
      <div>
        <p class="eyebrow">Source</p>
        <h2>Paste or upload the API</h2>
      </div>
    </div>

    <div class="field-group">
      <label class="field-label" for="input-type">Input type</label>
      <select id="input-type" :value="inputType" @change="$emit('update:inputType', $event.target.value)">
        <option v-for="option in inputTypeOptions" :key="option" :value="option">{{ option }}</option>
      </select>
    </div>

    <div class="field-group">
      <label class="field-label" for="file-input">Upload a file</label>
      <input id="file-input" type="file" accept=".yaml,.yml,.json,.md,.txt,.py" @change="handleFileChange" />
    </div>

    <div class="field-group spec-group">
      <label class="field-label" for="raw-content">Specification or requirement</label>
      <textarea
        id="raw-content"
        :value="rawContent"
        rows="6"
        placeholder="Paste an OpenAPI spec or describe the system in plain English."
        @input="$emit('update:rawContent', $event.target.value)"
      />
    </div>

    <div class="panel-actions">
      <button class="primary-button generate-button" type="button" :disabled="loading || !rawContent.trim()" @click="$emit('generate')">
        {{ loading ? 'Generating...' : 'Generate tests' }}
      </button>
    </div>
  </section>
</template>

<script setup>
const props = defineProps({
  inputType: {
    type: String,
    default: 'OpenAPI / Swagger',
  },
  rawContent: {
    type: String,
    default: '',
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:inputType', 'update:rawContent', 'generate'])

const inputTypeOptions = ['OpenAPI / Swagger', 'Plain English']

function handleFileChange(event) {
  const [file] = event.target.files || []
  if (!file) {
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    emit('update:rawContent', String(reader.result || ''))
  }
  reader.readAsText(file)
}
</script>
