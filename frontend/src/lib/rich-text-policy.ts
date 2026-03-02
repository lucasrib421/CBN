import DOMPurify from 'isomorphic-dompurify'

export const RICH_TEXT_ALLOWED_TAGS = [
  'p',
  'h2',
  'h3',
  'strong',
  'em',
  'ul',
  'ol',
  'li',
  'blockquote',
  'a',
  'hr',
  'figure',
  'img',
  'figcaption',
  'br',
]

export const RICH_TEXT_ALLOWED_ATTRIBUTES = ['href', 'target', 'rel', 'src', 'alt']

const SAFE_URI_PATTERN = /^(\/|#|https?:|mailto:)/i

export function sanitizeRichTextHtml(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: RICH_TEXT_ALLOWED_TAGS,
    ALLOWED_ATTR: RICH_TEXT_ALLOWED_ATTRIBUTES,
    FORBID_TAGS: ['script', 'style'],
    ALLOWED_URI_REGEXP: SAFE_URI_PATTERN,
  })
}

export function extractPlainTextFromRichText(html: string): string {
  const sanitized = sanitizeRichTextHtml(html)
  return sanitized
    .replace(/<[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}
