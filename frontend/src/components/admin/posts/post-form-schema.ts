import { z } from 'zod'

import { extractPlainTextFromRichText } from '@/lib/rich-text-policy'

const MIN_CONTENT_LENGTH = 10
const normalizeCheckboxValues = (value: unknown): unknown[] => {
  if (value === undefined || value === null || value === '' || value === false) {
    return []
  }

  const values = Array.isArray(value) ? value : [value]
  return values.filter((entry) => entry !== undefined && entry !== null && entry !== '' && entry !== false)
}

export const postFormSchema = z.object({
  title: z.string().min(3, 'O título deve ter pelo menos 3 caracteres'),
  subtitle: z.string().optional(),
  slug: z.string().min(3, 'O slug é obrigatório'),
  content: z
    .string()
    .refine(
      (value) => extractPlainTextFromRichText(value).length >= MIN_CONTENT_LENGTH,
      `O conteúdo deve ter pelo menos ${MIN_CONTENT_LENGTH} caracteres`,
    ),
  status: z.enum(['DRAFT', 'PUBLISHED', 'ARCHIVED']),
  categories: z.preprocess(
    normalizeCheckboxValues,
    z.array(z.coerce.number()).min(1, 'Selecione pelo menos uma categoria'),
  ),
  tags: z.preprocess(normalizeCheckboxValues, z.array(z.coerce.number())),
  cover_image: z.string().optional().nullable(),
  published_at: z.string().optional().nullable(),
})

export type PostFormData = z.infer<typeof postFormSchema>
