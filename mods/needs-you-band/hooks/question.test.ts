import { lastQuestion } from './question'
import { test, expect } from 'claude-code/testing'

test('finds a trailing question', () => expect(lastQuestion('Done.\n\nShould I build the rest?')).toBe('Should I build the rest?'))
test('none when no question', () => expect(lastQuestion('All done.')).toBeUndefined())
