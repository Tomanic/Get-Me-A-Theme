import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'
import { lastQuestion } from './question'
import type { Waiting } from '../types'

const waiting = atom({ plugin: 'needs-you-band', key: 'waiting' } as const, null as Waiting)

export const register: Register = on => {
  on('prompt.submit', async ($, e, next) => {
    await update($, waiting, () => null)
    return next(e)
  })

  on('tool.call', { tool: 'AskUserQuestion' }, async ($, e, next) => {
    $.ui.toast('Claude is waiting on your answer')
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    if (e.agentId === undefined && e.reason === 'answer') {
      const q = lastQuestion(e.answer)
      if (q) {
        await update($, waiting, () => q)
        $.ui.toast('Claude asked you something')
      }
    }
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const q = await read($, waiting)
    if (e.props.hasSurvey || q === null) return next(e)
    const { Box, Button, Text } = $.ui.resolve(e)
    return (
      <Box>
        <Text color="yellow">Waiting on you: {q} </Text>
        <Button key="dismiss" label="Dismiss" onPress={() => update($, waiting, () => null)} />
      </Box>
    )
  })
}
