export type Waiting = string | null

declare module 'claude-code' {
  interface PluginState {
    'needs-you-band': { waiting: Waiting }
  }
}
