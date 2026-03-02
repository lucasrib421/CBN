import { describe, expect, test } from 'vitest'

import { buildStatusOptions } from './workflow'

describe('workflow status options', () => {
  test('keeps current status and allowed transitions without duplicates', () => {
    const options = buildStatusOptions('DRAFT', ['REVIEW', 'PUBLISHED', 'REVIEW'])

    expect(options).toEqual([
      { value: 'DRAFT', label: 'Rascunho' },
      { value: 'REVIEW', label: 'Em revisão' },
      { value: 'PUBLISHED', label: 'Publicado' },
    ])
  })

  test('uses backend labels when available', () => {
    const options = buildStatusOptions('REVIEW', ['DRAFT'], {
      REVIEW: 'Em Revisão Editorial',
      DRAFT: 'Rascunho',
    })

    expect(options).toEqual([
      { value: 'REVIEW', label: 'Em Revisão Editorial' },
      { value: 'DRAFT', label: 'Rascunho' },
    ])
  })
})
