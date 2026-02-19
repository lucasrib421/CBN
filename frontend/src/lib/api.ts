const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const INTERNAL_API_URL = process.env.INTERNAL_API_URL || 'http://api:8000';

export async function fetchAPI<T>(path: string, options?: RequestInit & { revalidate?: number }): Promise<T> {
  const isServer = typeof window === 'undefined';
  const baseUrl = isServer ? INTERNAL_API_URL : API_URL;
  const { revalidate, ...fetchOptions } = options || {};
  
  const res = await fetch(`${baseUrl}/api/v1${path}`, {
    ...fetchOptions,
    next: revalidate !== undefined ? { revalidate } : undefined,
  });
  
  if (!res.ok) {
    if (res.status === 404) {
        throw new Error('Not Found');
    }
    throw new Error(`API error: ${res.status}`);
  }
  
  return res.json();
}
