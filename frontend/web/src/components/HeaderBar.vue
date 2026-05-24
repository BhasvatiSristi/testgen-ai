<template>
  <header class="hero-card header-bar">
    <div class="hero-copy">
      <p class="eyebrow">TestGen AI</p>
      <h1>TestGen AI</h1>
      <p class="lede">Paste, upload, or load the API to improve your test coverage. <span class="header-status">{{ status }}</span></p>
    </div>
  </header>
</template>

<script setup>
defineProps({
  status: {
    type: String,
    default: 'Ready to generate tests.',
  },
})
</script>
