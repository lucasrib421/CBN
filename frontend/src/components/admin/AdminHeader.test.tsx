import { render, screen } from '@testing-library/react';
import { expect, test, vi } from 'vitest';

// Mock next-auth/react
const mockSession = {
  data: {
    user: { name: 'Admin User', email: 'admin@example.com' },
    accessToken: 'mock-token',
    expires: '2099-01-01',
  },
  status: 'authenticated' as const,
  update: vi.fn(),
};

vi.mock('next-auth/react', () => ({
  useSession: () => mockSession,
  signOut: vi.fn(),
}));

import AdminHeader from './AdminHeader';

test('renders user name from session', () => {
  render(<AdminHeader />);
  expect(screen.getByText('Admin User')).toBeDefined();
});

test('renders sign out button', () => {
  render(<AdminHeader />);
  expect(screen.getByText('Sair')).toBeDefined();
});

test('renders fallback when no user name', () => {
  mockSession.data.user = { name: '', email: '' } as any;
  render(<AdminHeader />);
  expect(screen.getByText('Admin')).toBeDefined();
  // Restore
  mockSession.data.user = { name: 'Admin User', email: 'admin@example.com' } as any;
});
