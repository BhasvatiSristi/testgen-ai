<template>
  <section class="surface-card history-panel">
    <div class="section-heading">
      <div>
        <p class="eyebrow">History</p>
        <h2>Recent runs</h2>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  history: {
    type: Array,
    default: () => [],
  },
})
</script>
