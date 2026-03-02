import { describe, expect, test } from 'vitest'

import { extractPlainTextFromRichText, sanitizeRichTextHtml } from './rich-text-policy'

describe('rich text policy', () => {
  test('removes malicious scripts and javascript links', () => {
    const sanitized = sanitizeRichTextHtml(
      '<p onclick="alert(1)">Texto</p><script>alert(1)</script><a href="javascript:alert(1)">Link</a>',
    )

    expect(sanitized).not.toContain('<script')
    expect(sanitized).not.toContain('onclick=')
    expect(sanitized).not.toContain('javascript:')
  })

  test('keeps allowed formatting tags', () => {
    const sanitized = sanitizeRichTextHtml(
      '<h2>Titulo</h2><p><strong>forte</strong> <em>italico</em></p><blockquote>cita</blockquote>',
    )

    expect(sanitized).toContain('<h2>Titulo</h2>')
    expect(sanitized).toContain('<strong>forte</strong>')
    expect(sanitized).toContain('<em>italico</em>')
    expect(sanitized).toContain('<blockquote>cita</blockquote>')
  })

  test('keeps safe relative and anchor links', () => {
    const sanitized = sanitizeRichTextHtml(
      '<a href="/categoria/politica">Interno</a><a href="#topo">Topo</a>',
    )

    expect(sanitized).toContain('href="/categoria/politica"')
    expect(sanitized).toContain('href="#topo"')
  })

  test('extracts readable plain text', () => {
    const text = extractPlainTextFromRichText('<h2>Titulo</h2><p>um <strong>dois</strong></p>')
    expect(text).toBe('Titulo um dois')
  })
})
