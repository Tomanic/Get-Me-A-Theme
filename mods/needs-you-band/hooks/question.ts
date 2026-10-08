/** The last question Claude asked in its final text, or undefined if it asked none. */
export function lastQuestion(answer: string): string | undefined {
  const lines = answer.split('\n').map(l => l.trim()).filter(Boolean)
  for (let i = lines.length - 1; i >= 0 && i >= lines.length - 4; i--) {
    if (lines[i].endsWith('?')) return lines[i].replace(/[*_`#>]/g, '').slice(0, 140)
  }
  return undefined
}
