import type { Register } from 'claude-code'
import { FACTS } from './facts'

export const register: Register = on => {
  on('prompt.compose', async ($, e, next) => {
    const out = await next(e)
    return {
      sections: [
        ...out.sections,
        { id: `${$.plugin.name}:hosts`, text: FACTS, scope: 'session' as const },
      ],
    }
  })
}
