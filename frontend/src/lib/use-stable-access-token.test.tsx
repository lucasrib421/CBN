import { renderHook } from '@testing-library/react'
import { beforeEach, expect, test, vi } from 'vitest'
import { getSession } from 'next-auth/react'

import { useStableAccessToken } from './use-stable-access-token'

vi.mock('next-auth/react', () => ({
  getSession: vi.fn(),
}))

const mockedGetSession = vi.mocked(getSession)

beforeEach(() => {
  mockedGetSession.mockReset()
})

test('returns token from current session data when available', async () => {
  const { result } = renderHook(() => useStableAccessToken('hook-token'))
  const resolveAccessToken = result.current

  await expect(resolveAccessToken()).resolves.toBe('hook-token')
  expect(mockedGetSession).not.toHaveBeenCalled()
})

test('falls back to next-auth session endpoint when hook token is unavailable', async () => {
  mockedGetSession.mockResolvedValue({
    accessToken: 'session-token',
  } as any)

  const { result } = renderHook(() => useStableAccessToken(undefined))
  const resolveAccessToken = result.current

  await expect(resolveAccessToken()).resolves.toBe('session-token')
  await expect(resolveAccessToken()).resolves.toBe('session-token')
  expect(mockedGetSession).toHaveBeenCalledTimes(1)
})

test('throws explicit error when no access token can be resolved', async () => {
  mockedGetSession.mockResolvedValue(null)

  const { result } = renderHook(() => useStableAccessToken(undefined))
  const resolveAccessToken = result.current

  await expect(resolveAccessToken()).rejects.toThrow('Sessão expirada. Faça login novamente.')
})

test('clears stale token when access token disappears and re-fetches session token', async () => {
  mockedGetSession.mockResolvedValue({
    accessToken: 'session-token-renewed',
  } as any)

  const { result, rerender } = renderHook(
    ({ token }: { token?: string }) => useStableAccessToken(token),
    { initialProps: { token: 'old-hook-token' } },
  )

  await expect(result.current()).resolves.toBe('old-hook-token')

  rerender({ token: undefined })

  await expect(result.current()).resolves.toBe('session-token-renewed')
  expect(mockedGetSession).toHaveBeenCalledTimes(1)
})
