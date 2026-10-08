import type { Register } from 'claude-code'
import { line, warning, type Reading } from './format'

export const register: Register = on => {
  const warned = new Set<string>()

  on('session.measure', ($, e, next) => {
    const r: Reading = { usd: e.cost?.usd, percent: e.context.percent, limits: e.rateLimits }
    $.ui.status(line(r) || undefined)
    const w = warning(r, warned)
    if (w) $.ui.toast(w)
    return next(e)
  })
}
