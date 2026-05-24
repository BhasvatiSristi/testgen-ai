<template>
  <section class="surface-card history-panel">
    <div class="section-heading">
      <div>
        <p class="eyebrow">History</p>
        <h2>Recent runs</h2>
      </div>
      <span class="soft-chip">{{ history.length }} saved</span>
    </div>

    <div v-if="history.length" class="history-list">
      <article v-for="run in history" :key="run.id" class="history-row">
        <div class="history-copy">
          <strong>{{ run.timestamp }} · {{ run.framework }} · {{ run.coverage_pct }}%</strong>
          <p>{{ run.input_type }}</p>
          <p>{{ run.input_summary }}</p>
        </div>
        <div class="history-actions">
          <button class="ghost-button" type="button" @click="$emit('load-run', run.id)">Load</button>
          <button class="ghost-button danger" type="button" @click="$emit('delete-run', run.id)">Delete</button>
        </div>
      </article>
    </div>
    <p v-else class="helper-text">No saved runs yet.</p>
  </section>
</template>

<script setup>
defineProps({
  history: {
    type: Array,
    default: () => [],
  },
})

defineEmits(['load-run', 'delete-run'])
</script>
