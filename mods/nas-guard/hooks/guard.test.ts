import { check } from './guard'
import { test, expect } from 'claude-code/testing'

test('blocks rm -rf under /volume1', () => expect(check('rm -rf /volume1/music/x')).toBeDefined())
test('blocks docker system prune', () => expect(check('docker system prune -af')).toBeDefined())
test('allows mv to #recycle', () => expect(check('mv /volume1/music/a /volume1/music/#recycle/')).toBeUndefined())
test('allows ls', () => expect(check('ls /volume1')).toBeUndefined())
