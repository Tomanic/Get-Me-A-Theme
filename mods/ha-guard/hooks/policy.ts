export type Seen = { read: boolean; backup: boolean }

const HA = 'mcp__home_assistant__'

export function note(tool: string, seen: Seen): void {
  if (tool === `${HA}ha_config_get_automation`) seen.read = true
  if (tool === `${HA}ha_manage_backup`) seen.backup = true
}

export function judge(tool: string, seen: Seen): string | undefined {
  if (tool === `${HA}ha_config_set_automation` && !seen.read) {
    return 'read the existing automation first (ha_config_get_automation) so nothing is overwritten blind'
  }
  if (tool === `${HA}ha_call_delete_tool` && !seen.backup) {
    return 'take a backup first (ha_manage_backup) so the delete can be undone'
  }
  return undefined
}
