'use client'

import { useCallback, useEffect, useRef } from 'react'
import { getSession } from 'next-auth/react'

const EXPIRED_SESSION_ERROR = 'Sessão expirada. Faça login novamente.'

export function useStableAccessToken(accessToken?: string) {
  const tokenRef = useRef<string | null>(accessToken || null)

  useEffect(() => {
    tokenRef.current = accessToken || null
  }, [accessToken])

  return useCallback(async () => {
    if (tokenRef.current) {
      return tokenRef.current
    }

    const session = await getSession()
    if (session?.accessToken) {
      tokenRef.current = session.accessToken
      return session.accessToken
    }

    throw new Error(EXPIRED_SESSION_ERROR)
  }, [])
}
