import type { Register } from 'claude-code'
import { check } from './guard'

export const register: Register = on => {
  on('tool.call', { tool: 'Bash' }, ($, e, next) => {
    const why = check(e.command)
    return why
      ? { deny: `${$.plugin.name}: blocked (${why}). Move files to #recycle instead, or ask Tom to run it himself.` }
      : next(e)
  }).catch(($, e, next) =>
    next.called ? next(e) : { deny: `${$.plugin.name}: its guard failed; not running the command.` },
  )
}
