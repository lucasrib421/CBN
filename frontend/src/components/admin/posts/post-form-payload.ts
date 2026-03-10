import { AdminPostWrite } from '@/types'

import { PostFormData } from './post-form-schema'
import { normalizeRelatedIds } from './post-form-normalizers'

export function buildPostWritePayload(data: PostFormData): AdminPostWrite {
  return {
    ...data,
    categories: normalizeRelatedIds(data.categories),
    cover_image: data.cover_image ? parseInt(data.cover_image, 10) : null,
    tags: normalizeRelatedIds(data.tags),
    published_at: data.status === 'PUBLISHED' ? (data.published_at || null) : null,
  }
}
