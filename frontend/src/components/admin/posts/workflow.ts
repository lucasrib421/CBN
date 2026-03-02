import { EditorialStatus } from '@/types'

export interface StatusOption {
  value: EditorialStatus
  label: string
}

export const STATUS_LABELS: Record<EditorialStatus, string> = {
  DRAFT: 'Rascunho',
  REVIEW: 'Em revisão',
  PUBLISHED: 'Publicado',
  ARCHIVED: 'Arquivado',
}

export function buildStatusOptions(
  currentStatus: EditorialStatus,
  allowedTransitions: EditorialStatus[],
  labels?: Record<string, string>,
): StatusOption[] {
  const options = new Set<EditorialStatus>([currentStatus, ...allowedTransitions])
  return Array.from(options).map((value) => ({
    value,
    label: labels?.[value] || STATUS_LABELS[value],
  }))
}
