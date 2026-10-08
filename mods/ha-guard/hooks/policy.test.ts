import { judge, note } from './policy'
import { test, expect } from 'claude-code/testing'

const HA = 'mcp__home_assistant__'

test('set needs a prior read', () => {
  const seen = { read: false, backup: false }
  expect(judge(`${HA}ha_config_set_automation`, seen)).toBeDefined()
  note(`${HA}ha_config_get_automation`, seen)
  expect(judge(`${HA}ha_config_set_automation`, seen)).toBeUndefined()
})
test('delete needs a prior backup', () => {
  const seen = { read: false, backup: false }
  expect(judge(`${HA}ha_call_delete_tool`, seen)).toBeDefined()
  note(`${HA}ha_manage_backup`, seen)
  expect(judge(`${HA}ha_call_delete_tool`, seen)).toBeUndefined()
})
test('other tools pass', () => expect(judge(`${HA}ha_search`, { read: false, backup: false })).toBeUndefined())
