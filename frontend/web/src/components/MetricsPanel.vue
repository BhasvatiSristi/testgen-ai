<template>
  <section class="metrics-grid">
    <article class="metric-card">
      <span class="metric-label">Tests generated</span>
      <strong>{{ metrics.testsGenerated }}</strong>
    </article>
    <article class="metric-card">
      <span class="metric-label">Endpoints covered</span>
      <strong>{{ metrics.coveredEndpoints }}</strong>
    </article>
    <article class="metric-card">
      <span class="metric-label">Coverage</span>
      <strong>{{ metrics.coveragePct }}%</strong>
    </article>
    <article class="metric-card">
      <span class="metric-label">Missing checks</span>
      <strong>{{ metrics.gapCount }}</strong>
    </article>
  </section>
</template>

<script setup>
defineProps({
  metrics: {
    type: Object,
    default: () => ({
      testsGenerated: 0,
      coveredEndpoints: 0,
      coveragePct: 0,
      gapCount: 0,
    }),
  },
})
</script>
