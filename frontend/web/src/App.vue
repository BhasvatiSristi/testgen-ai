<template>
  <div class="app-shell">
    <HeaderBar :status="state.error || state.status" />

    <section class="top-grid">
      <aside class="top-left-rail">
        <SourcePanel
          v-model:inputType="state.inputType"
          v-model:rawContent="state.rawContent"
          :loading="state.loading"
          @generate="generate"
        />
      </aside>

      <aside class="top-right-rail">
        <ConfigPanel
          v-model:framework="state.framework"
          v-model:testTypes="state.testTypes"
          v-model:coverageDepth="state.coverageDepth"
        />
        <MetricsPanel :metrics="metrics" />
      </aside>
    </section>

    <section class="lower-grid">
      <div class="preview-column">
        <OutputWorkspace :generatedTests="state.generatedTests" :framework="state.framework" />
      </div>

      <aside class="insight-column">
        <div class="insight-main">
          <CoveragePanel :coverage="state.coverage" :coverageGaps="state.coverageGaps" @generate-gap="handleGapGeneration" />
        </div>
        <div class="insight-side">
          <HistoryPanel />
        </div>
      </aside>
    </section>

    <footer class="footer-grid">
      <ExportPanel
        v-model:repo="state.repo"
        v-model:token="state.token"
        :generatedTests="state.generatedTests"
        :framework="state.framework"
        :exporting="state.exporting"
        @export-github="pushGithub"
      />
    </footer>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

import ConfigPanel from './components/ConfigPanel.vue'
import CoveragePanel from './components/CoveragePanel.vue'
import ExportPanel from './components/ExportPanel.vue'
import HeaderBar from './components/HeaderBar.vue'
import HistoryPanel from './components/HistoryPanel.vue'
import MetricsPanel from './components/MetricsPanel.vue'
import OutputWorkspace from './components/OutputWorkspace.vue'
import SourcePanel from './components/SourcePanel.vue'
import { useTestGen } from './composables/useTestGen'

const { state, metrics, bootstrap, generate, pushGithub } = useTestGen()

async function handleGapGeneration(gap) {
  await generate({
    focus_endpoint: gap.endpoint || '',
    pending_gap_scenario: gap,
  })
}

onMounted(() => {
  bootstrap()
})
</script>
