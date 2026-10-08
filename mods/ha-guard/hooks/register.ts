import type { Register } from 'claude-code'
import { judge, note, type Seen } from './policy'

export const register: Register = on => {
  const seen: Seen = { read: false, backup: false }

  on('tool.call', { tool: /^mcp__home_assistant__/ }, ($, e, next) => {
    const why = judge(e.tool, seen)
    if (why) return { deny: `${$.plugin.name}: ${why}.` }
    note(e.tool, seen)
    return next(e)
  }).catch(($, e, next) =>
    next.called ? next(e) : { deny: `${$.plugin.name}: its guard failed; not running the Home Assistant call.` },
  )
}
