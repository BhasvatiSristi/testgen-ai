<template>
  <section class="surface-card source-panel">
    <div class="section-heading">
      <div>
        <p class="eyebrow">Source</p>
        <h2>Paste, upload, or load a demo</h2>
      </div>
      <span class="soft-chip">{{ selectedDemoName || 'No demo selected' }}</span>
    </div>

    <div class="field-group">
      <label class="field-label" for="input-type">Input type</label>
      <select id="input-type" :value="inputType" @change="$emit('update:inputType', $event.target.value)">
        <option v-for="option in inputTypeOptions" :key="option" :value="option">{{ option }}</option>
      </select>
    </div>

    <div class="field-group">
      <label class="field-label">Demo examples</label>
      <div class="demo-grid">
        <button
          v-for="demo in demos"
          :key="demo.name"
          class="demo-chip"
          type="button"
          :class="{ active: demo.name === selectedDemoName }"
          @click="$emit('select-demo', demo.name)"
        >
          <strong>{{ demo.name }}</strong>
          <span>{{ demo.description }}</span>
        </button>
      </div>
    </div>

    <div class="field-group">
      <label class="field-label" for="file-input">Upload a file</label>
      <input id="file-input" type="file" accept=".yaml,.yml,.json,.md,.txt,.py" @change="handleFileChange" />
      <p class="helper-text">The file is read locally in the browser before it is sent to the API.</p>
    </div>

    <div class="field-group">
      <label class="field-label" for="raw-content">Specification or requirement</label>
      <textarea
        id="raw-content"
        :value="rawContent"
        rows="14"
        placeholder="Paste an OpenAPI spec or describe the system in plain English."
        @input="$emit('update:rawContent', $event.target.value)"
      />
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
  demos: {
    type: Array,
    default: () => [],
  },
  selectedDemoName: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:inputType', 'update:rawContent', 'select-demo'])

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
