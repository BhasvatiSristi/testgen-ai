import { computed, reactive } from 'vue'

import { copyText, downloadText } from '../lib/download'
import {
  deleteHistoryRun,
  exportGithub,
  generateTests,
  getDemos,
  getHistory,
  getHistoryRun,
} from '../lib/api'

const SECTION_ORDER = ['unit', 'integration', 'edge_cases']

function countTests(generatedTests) {
  const combinedText = SECTION_ORDER.map((section) => generatedTests[section] || '').join('\n')
  const matches = combinedText.match(/^\s*(?:def\s+test_|it\s*\(|test\s*\(|@Test\b)/gim)
  return matches ? matches.length : 0
}

function sectionFileName(section, framework) {
  const frameworkSuffix = {
    pytest: 'py',
    jest: 'js',
    junit: 'java',
    rspec: 'rb',
  }[framework] || 'txt'

  return {
    unit: `unit_tests.${frameworkSuffix}`,
    integration: `integration_tests.${frameworkSuffix}`,
    edge_cases: `edge_case_tests.${frameworkSuffix}`,
  }[section]
}

export function useTestGen() {
  const state = reactive({
    inputType: 'OpenAPI / Swagger',
    rawContent: '',
    framework: 'pytest',
    testTypes: ['Unit tests', 'Integration tests', 'Edge cases'],
    coverageDepth: 2,
    selectedDemoName: '',
    repo: '',
    token: '',
    generatedTests: {
      unit: '',
      integration: '',
      edge_cases: '',
    },
    coverage: {
      total_endpoints: 0,
      covered: 0,
      uncovered: [],
      coverage_pct: 0,
    },
    coverageGaps: [],
    demos: [],
    history: [],
    loading: false,
    exporting: false,
    error: '',
    status: 'Ready to generate tests.',
  })

  const metrics = computed(() => ({
    testsGenerated: countTests(state.generatedTests),
    coveredEndpoints: state.coverage.covered || 0,
    coveragePct: state.coverage.coverage_pct || 0,
    uncoveredEndpoints: (state.coverage.uncovered || []).length,
    totalEndpoints: state.coverage.total_endpoints || 0,
    gapCount: (state.coverageGaps || []).length,
  }))

  async function bootstrap() {
    try {
      const [demos, history] = await Promise.all([getDemos(), getHistory()])
      state.demos = demos
      state.history = history

      if (!state.rawContent && demos.length > 0) {
        const firstDemo = demos[0]
        state.selectedDemoName = firstDemo.name || ''
        state.inputType = firstDemo.input_type || state.inputType
        state.rawContent = firstDemo.content || ''
        state.status = `Loaded demo: ${state.selectedDemoName}.`
      }
    } catch (error) {
      state.error = error instanceof Error ? error.message : String(error)
    }
  }

  function setDemoByName(name) {
    const selected = state.demos.find((demo) => demo.name === name)
    if (!selected) {
      return
    }

    state.selectedDemoName = selected.name || ''
    state.inputType = selected.input_type || state.inputType
    state.rawContent = selected.content || ''
    state.status = `Loaded demo: ${selected.name}.`
  }

  async function refreshHistory() {
    state.history = await getHistory()
  }

  async function generate(overrides = {}) {
    if (!state.rawContent.trim()) {
      state.error = 'Please provide an OpenAPI document or a plain-English description.'
      return
    }

    state.loading = true
    state.error = ''

    try {
      const payload = {
        input_type: state.inputType,
        raw_content: state.rawContent,
        framework: state.framework,
        test_types: state.testTypes,
        coverage_depth: state.coverageDepth,
        focus_endpoint: overrides.focus_endpoint || '',
        pending_gap_scenario: overrides.pending_gap_scenario || null,
      }

      const response = await generateTests(payload)
      const generated = response.generated_tests || {}

      state.generatedTests.unit = generated.unit || ''
      state.generatedTests.integration = generated.integration || ''
      state.generatedTests.edge_cases = generated.edge_cases || ''
      state.coverage = response.coverage || state.coverage
      state.coverageGaps = response.coverage_gaps || []
      state.status = `Generated ${state.framework} tests with ${state.coverage.coverage_pct || 0}% coverage.`

      await refreshHistory()
    } catch (error) {
      state.error = error instanceof Error ? error.message : String(error)
    } finally {
      state.loading = false
    }
  }

  async function loadHistoryRun(runId) {
    const run = await getHistoryRun(runId)

    state.generatedTests.unit = run.unit_tests || ''
    state.generatedTests.integration = run.integration_tests || ''
    state.generatedTests.edge_cases = run.edge_cases || ''
    state.coverage = {
      total_endpoints: 0,
      covered: 0,
      uncovered: [],
      coverage_pct: Number(run.coverage_pct || 0),
    }
    state.coverageGaps = []
    state.framework = run.framework || state.framework
    state.inputType = run.input_type || state.inputType
    state.status = `Loaded run #${run.id}.`
  }

  async function removeHistoryRun(runId) {
    await deleteHistoryRun(runId)
    await refreshHistory()
    state.status = `Deleted run #${runId}.`
  }

  async function pushGithub() {
    if (!state.repo.trim() || !state.token.trim()) {
      state.error = 'Provide both a GitHub repo and token.'
      return null
    }

    state.exporting = true
    state.error = ''

    try {
      const response = await exportGithub({
        repo: state.repo,
        token: state.token,
        framework: state.framework,
        tests: state.generatedTests,
      })

      if (response.success) {
        state.status = 'Pushed generated tests to GitHub.'
        return response
      }

      throw new Error(response.error || 'GitHub push failed.')
    } catch (error) {
      state.error = error instanceof Error ? error.message : String(error)
      return null
    } finally {
      state.exporting = false
    }
  }

  async function copyAllTests() {
    const combined = SECTION_ORDER.map((section) => `# ${section.replace('_', ' ')}\n${state.generatedTests[section] || ''}`).join('\n\n')
    await copyText(combined)
    state.status = 'Copied the generated tests to the clipboard.'
  }

  function downloadSection(section) {
    downloadText(sectionFileName(section, state.framework), state.generatedTests[section] || '')
  }

  return {
    state,
    metrics,
    bootstrap,
    setDemoByName,
    generate,
    loadHistoryRun,
    removeHistoryRun,
    pushGithub,
    copyAllTests,
    downloadSection,
  }
}
