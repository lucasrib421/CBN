import { expect, test, vi, beforeEach } from 'vitest';

// Mock the auth module
vi.mock('@/auth', () => ({
  auth: vi.fn().mockResolvedValue({
    accessToken: 'test-token-123',
    user: { name: 'Test Admin' },
    expires: '2099-01-01',
  }),
}));

// Mock global fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

import { fetchAdminAPIClient, AuthError } from './admin-api';

beforeEach(() => {
  mockFetch.mockReset();
});

test('fetchAdminAPIClient sends auth header', async () => {
  mockFetch.mockResolvedValueOnce({
    ok: true,
    json: () => Promise.resolve({ results: [], count: 0 }),
  });

  await fetchAdminAPIClient('/posts/', 'my-token');

  expect(mockFetch).toHaveBeenCalledWith(
    expect.stringContaining('/api/v1/painel/posts/'),
    expect.objectContaining({
      headers: expect.objectContaining({
        Authorization: 'Bearer my-token',
        'Content-Type': 'application/json',
      }),
    })
  );
});

test('fetchAdminAPIClient skips Content-Type for FormData', async () => {
  const formData = new FormData();
  formData.append('file', new Blob(['test']), 'test.png');

  mockFetch.mockResolvedValueOnce({
    ok: true,
    json: () => Promise.resolve({ id: 1 }),
  });

  await fetchAdminAPIClient('/media/', 'my-token', {
    method: 'POST',
    body: formData,
  });

  const callHeaders = mockFetch.mock.calls[0][1].headers;
  expect(callHeaders['Content-Type']).toBeUndefined();
  expect(callHeaders['Authorization']).toBe('Bearer my-token');
});

test('fetchAdminAPIClient throws on non-ok response', async () => {
  mockFetch.mockResolvedValueOnce({
    ok: false,
    status: 403,
    text: () => Promise.resolve('Forbidden'),
  });

  await expect(
    fetchAdminAPIClient('/posts/', 'my-token')
  ).rejects.toThrow('API error 403: Forbidden');
});

test('AuthError has status property', () => {
  const err = new AuthError('Unauthorized', 401);
  expect(err.message).toBe('Unauthorized');
  expect(err.status).toBe(401);
  expect(err.name).toBe('AuthError');
});
