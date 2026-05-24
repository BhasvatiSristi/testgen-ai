<template>
  <header class="hero-card header-bar">
    <div class="hero-copy">
      <p class="eyebrow">TestGen AI</p>
      <h1>Warm-toned Vue UI for AI test generation.</h1>
      <p class="lede">
        Generate unit, integration, and edge-case suites from OpenAPI specs or plain-English requirements.
      </p>
    </div>

    <div class="header-actions">
      <div class="status-stack">
        <span class="status-pill">{{ status }}</span>
        <span class="mini-note">{{ loading ? 'Working through the prompt chain...' : 'Ready for a new run.' }}</span>
      </div>
      <button class="primary-button" :disabled="loading" @click="$emit('generate')">
        {{ loading ? 'Generating...' : 'Generate tests' }}
      </button>
    </div>
  </header>
</template>

<script setup>
defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
  status: {
    type: String,
    default: 'Ready to generate tests.',
  },
})

defineEmits(['generate'])
</script>
