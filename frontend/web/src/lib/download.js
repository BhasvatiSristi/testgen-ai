export function downloadText(filename, content) {
  const blob = new Blob([content ?? ''], { type: 'text/plain;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const anchor = document.createElement('a')

  anchor.href = url
  anchor.download = filename
  anchor.click()

  window.URL.revokeObjectURL(url)
}

export async function copyText(text) {
  await navigator.clipboard.writeText(text ?? '')
}
