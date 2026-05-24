<template>
  <section class="surface-card coverage-panel">
    <div class="section-heading">
      <div>
        <p class="eyebrow">Coverage</p>
        <h2>What still needs work</h2>
      </div>
      <span class="soft-chip">{{ coverage.coverage_pct || 0 }}%</span>
    </div>

    <div class="coverage-summary">
      <div>
        <span class="metric-label">Covered</span>
        <strong>{{ coverage.covered || 0 }}</strong>
      </div>
      <div>
        <span class="metric-label">Uncovered</span>
        <strong>{{ uncoveredEndpoints.length }}</strong>
      </div>
      <div>
        <span class="metric-label">Total</span>
        <strong>{{ coverage.total_endpoints || 0 }}</strong>
      </div>
    </div>

    <div v-if="uncoveredEndpoints.length" class="coverage-list">
      <article v-for="endpoint in uncoveredEndpoints" :key="endpoint" class="coverage-row warning-row">
        <div>
          <strong>Uncovered endpoint</strong>
          <p>{{ endpoint }}</p>
        </div>
        <button
          class="ghost-button"
          type="button"
          @click="$emit('generate-gap', { endpoint, missing_scenario: `Generate focused tests for ${endpoint}`, priority: 'high' })"
        >
          Generate missing tests
        </button>
      </article>
    </div>
    <p v-else class="helper-text">No uncovered endpoints yet.</p>

    <div class="gap-section">
      <h3>Gap suggestions</h3>
      <div v-if="coverageGaps.length" class="gap-list">
        <article
          v-for="gap in coverageGaps"
          :key="`${gap.endpoint}-${gap.missing_scenario}`"
          class="gap-row"
          :class="`priority-${gap.priority || 'medium'}`"
        >
          <span class="gap-badge">{{ gap.priority || 'medium' }}</span>
          <div>
            <strong>{{ gap.endpoint }}</strong>
            <p>{{ gap.missing_scenario }}</p>
          </div>
          <button class="ghost-button" type="button" @click="$emit('generate-gap', gap)">Generate this test</button>
        </article>
      </div>
      <p v-else class="helper-text">No gap suggestions available yet.</p>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  coverage: {
    type: Object,
    default: () => ({ total_endpoints: 0, covered: 0, uncovered: [], coverage_pct: 0 }),
  },
  coverageGaps: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['generate-gap'])

const uncoveredEndpoints = computed(() => (Array.isArray(props.coverage?.uncovered) ? props.coverage.uncovered : []))
</script>
