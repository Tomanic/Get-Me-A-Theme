export type Reading = {
  usd?: number
  percent?: number
  limits: { kind: string; percentUsed: number }[]
}

export function line(r: Reading): string {
  const parts: string[] = []
  if (r.usd !== undefined) parts.push(`$${r.usd.toFixed(2)}`)
  if (r.percent !== undefined) parts.push(`ctx ${Math.round(r.percent)}%`)
  for (const l of r.limits) parts.push(`${l.kind === 'five_hour' ? '5h' : l.kind === 'seven_day' ? '7d' : l.kind} ${Math.round(l.percentUsed)}%`)
  return parts.join(' · ')
}

/** Returns a warning when a threshold is first crossed; `warned` remembers which. */
export function warning(r: Reading, warned: Set<string>): string | undefined {
  const check = (key: string, hit: boolean, text: string) => {
    if (!hit || warned.has(key)) return undefined
    warned.add(key)
    return text
  }
  return (
    check('ctx90', (r.percent ?? 0) >= 90, 'Context is 90% full: compact or start a fresh session') ??
    check('ctx75', (r.percent ?? 0) >= 75, 'Context is 75% full') ??
    check('usd20', (r.usd ?? 0) >= 20, 'This session has cost over $20') ??
    check('usd5', (r.usd ?? 0) >= 5, 'This session has cost over $5')
  )
}
