<template>
  <div class="app-shell">
    <HeaderBar :loading="state.loading" :status="state.status" @generate="generate" />

    <p v-if="state.error" class="banner banner-error">{{ state.error }}</p>
    <p v-else-if="state.status" class="banner banner-soft">{{ state.status }}</p>

    <div class="workspace-grid">
      <aside class="left-rail">
        <SourcePanel
          v-model:inputType="state.inputType"
          v-model:rawContent="state.rawContent"
          :demos="state.demos"
          :selectedDemoName="state.selectedDemoName"
          @select-demo="handleDemoSelection"
        />

        <ConfigPanel
          v-model:framework="state.framework"
          v-model:testTypes="state.testTypes"
          v-model:coverageDepth="state.coverageDepth"
        />
      </aside>

      <main class="right-rail">
        <MetricsPanel :metrics="metrics" />

        <div class="content-grid">
          <OutputWorkspace :generatedTests="state.generatedTests" :framework="state.framework" />
          <CoveragePanel :coverage="state.coverage" :coverageGaps="state.coverageGaps" @generate-gap="handleGapGeneration" />
        </div>

        <ExportPanel
          v-model:repo="state.repo"
          v-model:token="state.token"
          :generatedTests="state.generatedTests"
          :framework="state.framework"
          :exporting="state.exporting"
          @export-github="pushGithub"
        />

        <HistoryPanel :history="state.history" @load-run="loadHistoryRun" @delete-run="removeHistoryRun" />
      </main>
    </div>
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

const { state, metrics, bootstrap, setDemoByName, generate, loadHistoryRun, removeHistoryRun, pushGithub } = useTestGen()

function handleDemoSelection(name) {
  setDemoByName(name)
}

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
