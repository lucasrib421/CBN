export function normalizeRelatedIds(values: unknown): number[] {
  const entries = Array.isArray(values) ? values : [values]
  return entries
    .map((entry) => Number(entry))
    .filter((entry) => Number.isInteger(entry) && entry > 0)
}
