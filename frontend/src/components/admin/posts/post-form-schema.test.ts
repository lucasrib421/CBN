import { describe, expect, test } from 'vitest'

import { postFormSchema } from './post-form-schema'

const validFormInput = {
  title: 'Título válido',
  subtitle: 'Subtítulo',
  slug: 'titulo-valido',
  content: '<p>Conteúdo com tamanho suficiente para passar.</p>',
  status: 'DRAFT' as const,
  cover_image: '',
  published_at: null,
}

describe('postFormSchema', () => {
  test('coerces category and tag ids from string values', () => {
    const parsed = postFormSchema.parse({
      ...validFormInput,
      categories: '6',
      tags: '3',
    })

    expect(parsed.categories).toEqual([6])
    expect(parsed.tags).toEqual([3])
  })

  test('rejects post without categories', () => {
    const result = postFormSchema.safeParse({
      ...validFormInput,
      categories: [],
      tags: [],
    })

    expect(result.success).toBe(false)
    if (result.success) {
      throw new Error('Expected schema validation to fail without categories')
    }
    expect(result.error.issues[0]?.message).toContain('Selecione pelo menos uma categoria')
  })

  test('normalizes unchecked tags to empty list instead of id zero', () => {
    const parsed = postFormSchema.parse({
      ...validFormInput,
      categories: '6',
      tags: false,
    })

    expect(parsed.tags).toEqual([])
  })
})
