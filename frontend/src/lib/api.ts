const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const INTERNAL_API_URL = process.env.INTERNAL_API_URL || 'http://api:8000';

// 1. Adicionamos 'tags?: string[]' na tipagem das opções
export async function fetchAPI<T>(
  path: string, 
  options?: RequestInit & { revalidate?: number; tags?: string[] }
): Promise<T> {
  const isServer = typeof window === 'undefined';
  const baseUrl = isServer ? INTERNAL_API_URL : API_URL;
  
  // 2. Extraímos 'tags' e 'revalidate' de dentro de options
  const { revalidate, tags, ...fetchOptions } = options || {};
  
  const res = await fetch(`${baseUrl}/api/v1${path}`, {
    ...fetchOptions,
    // 3. Construímos o objeto 'next' dinamicamente
    next: {
      ...(revalidate !== undefined && { revalidate }),
      ...(tags !== undefined && { tags }),
    },
  });
  
  if (!res.ok) {
    if (res.status === 404) {
        throw new Error('Not Found');
    }
    throw new Error(`API error: ${res.status}`);
  }
  
  return res.json();
}