import { render, screen } from '@testing-library/react';
import { expect, test, vi } from 'vitest';

// Mock next-auth/react SessionProvider
vi.mock('next-auth/react', () => ({
  SessionProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="session-provider">{children}</div>
  ),
}));

import AdminProviders from './providers';

test('wraps children in SessionProvider', () => {
  render(
    <AdminProviders>
      <span>Test Child</span>
    </AdminProviders>
  );

  expect(screen.getByTestId('session-provider')).toBeDefined();
  expect(screen.getByText('Test Child')).toBeDefined();
});
