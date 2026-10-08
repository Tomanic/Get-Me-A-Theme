import { line, warning } from './format'
import { test, expect } from 'claude-code/testing'

test('formats the line', () =>
  expect(line({ usd: 1.234, percent: 45.4, limits: [{ kind: 'five_hour', percentUsed: 30 }] })).toBe('$1.23 · ctx 45% · 5h 30%'))
test('warns once per threshold', () => {
  const w = new Set<string>()
  expect(warning({ percent: 80, limits: [] }, w)).toBe('Context is 75% full')
  expect(warning({ percent: 80, limits: [] }, w)).toBeUndefined()
  expect(warning({ percent: 95, limits: [] }, w)).toContain('90%')
})
