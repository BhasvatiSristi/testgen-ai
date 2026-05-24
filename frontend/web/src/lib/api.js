const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  const text = await response.text()
  let payload = {}

  if (text) {
    try {
      payload = JSON.parse(text)
    } catch {
      payload = { detail: text }
    }
  }

  if (!response.ok) {
    throw new Error(payload.detail || payload.error || `Request failed with status ${response.status}`)
  }

  return payload
}

export async function getDemos() {
  const payload = await requestJson('/api/demos')
  return payload.demos || []
}

export async function getHistory() {
  const payload = await requestJson('/api/history')
  return payload.runs || []
}

export async function getHistoryRun(runId) {
  return requestJson(`/api/history/${runId}`)
}

export async function deleteHistoryRun(runId) {
  return requestJson(`/api/history/${runId}`, { method: 'DELETE' })
}

export async function generateTests(body) {
  return requestJson('/api/generate', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function exportGithub(body) {
  return requestJson('/api/export/github', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}
