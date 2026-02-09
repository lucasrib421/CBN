import { auth } from "@/auth"

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const INTERNAL_API_URL = process.env.INTERNAL_API_URL || 'http://api:8000'

export class AuthError extends Error {
  constructor(message: string, public status: number) {
    super(message)
    this.name = 'AuthError'
  }
}

export async function fetchAdminAPI<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const session = await auth()
  
  if (!session?.accessToken) {
    throw new AuthError('Not authenticated', 401)
  }

  const isServer = typeof window === 'undefined'
  const baseUrl = isServer ? INTERNAL_API_URL : API_URL

  const res = await fetch(`${baseUrl}/api/v1/painel${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${session.accessToken}`,
      ...options?.headers,
    },
    cache: 'no-store',
  })

  if (res.status === 401) {
    throw new AuthError('Token expired or invalid', 401)
  }

  if (!res.ok) {
    const error = await res.text()
    throw new Error(`API error ${res.status}: ${error}`)
  }

  return res.json()
}

// Client-side version that takes token as parameter
export async function fetchAdminAPIClient<T>(
  path: string,
  token: string,
  options?: RequestInit
): Promise<T> {
  const isFormData = options?.body instanceof FormData
  const headers: Record<string, string> = {
    Authorization: `Bearer ${token}`,
  }
  if (!isFormData) {
    headers['Content-Type'] = 'application/json'
  }

  const res = await fetch(`${API_URL}/api/v1/painel${path}`, {
    ...options,
    headers: {
      ...headers,
      ...(options?.headers as Record<string, string>),
    },
  })

  if (!res.ok) {
    const error = await res.text()
    throw new Error(`API error ${res.status}: ${error}`)
  }

  return res.json()
}
