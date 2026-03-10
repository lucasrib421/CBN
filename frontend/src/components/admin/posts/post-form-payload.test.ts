import { describe, expect, test } from 'vitest'

import { buildPostWritePayload } from './post-form-payload'

describe('buildPostWritePayload', () => {
  test('clears published_at when status is not published', () => {
    expect(
      buildPostWritePayload({
        title: 'Titulo',
        subtitle: 'Subtitulo',
        slug: 'titulo',
        content: '<p>Conteudo suficiente</p>',
        status: 'DRAFT',
        published_at: '2026-03-10T10:56',
        categories: [1, '2'],
        tags: ['3'],
        cover_image: '4',
      }),
    ).toEqual({
      title: 'Titulo',
      subtitle: 'Subtitulo',
      slug: 'titulo',
      content: '<p>Conteudo suficiente</p>',
      status: 'DRAFT',
      published_at: null,
      categories: [1, 2],
      tags: [3],
      cover_image: 4,
    })
  })

  test('preserves published_at when status is published', () => {
    expect(
      buildPostWritePayload({
        title: 'Titulo',
        subtitle: 'Subtitulo',
        slug: 'titulo',
        content: '<p>Conteudo suficiente</p>',
        status: 'PUBLISHED',
        published_at: '2026-03-10T10:56',
        categories: [1],
        tags: [],
        cover_image: null,
      }),
    ).toEqual({
      title: 'Titulo',
      subtitle: 'Subtitulo',
      slug: 'titulo',
      content: '<p>Conteudo suficiente</p>',
      status: 'PUBLISHED',
      published_at: '2026-03-10T10:56',
      categories: [1],
      tags: [],
      cover_image: null,
    })
  })
})
