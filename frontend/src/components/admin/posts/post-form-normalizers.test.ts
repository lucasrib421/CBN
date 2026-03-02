import { describe, expect, test } from 'vitest'

import { normalizeRelatedIds } from './post-form-normalizers'

describe('normalizeRelatedIds', () => {
  test('keeps only positive integer ids', () => {
    expect(normalizeRelatedIds([1, '2', 0, -1, 'abc', null, undefined, false])).toEqual([1, 2])
  })

  test('normalizes single values to array', () => {
    expect(normalizeRelatedIds('7')).toEqual([7])
    expect(normalizeRelatedIds(false)).toEqual([])
  })
})
