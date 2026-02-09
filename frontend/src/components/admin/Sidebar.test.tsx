import { render, screen, fireEvent } from '@testing-library/react';
import { expect, test, vi, beforeEach } from 'vitest';

// Mock next/navigation
const mockPathname = vi.fn(() => '/admin');
vi.mock('next/navigation', () => ({
  usePathname: () => mockPathname(),
}));

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href, className, onClick }: { children: React.ReactNode; href: string; className?: string; onClick?: () => void }) => (
    <a href={href} className={className} onClick={onClick}>{children}</a>
  ),
}));

import Sidebar from './Sidebar';

beforeEach(() => {
  mockPathname.mockReturnValue('/admin');
});

test('renders all navigation items', () => {
  render(<Sidebar />);

  expect(screen.getByText('CBN Admin')).toBeDefined();
  expect(screen.getByText('Dashboard')).toBeDefined();
  expect(screen.getByText('Publicações')).toBeDefined();
  expect(screen.getByText('Mídia')).toBeDefined();
  expect(screen.getByText('Categorias')).toBeDefined();
  expect(screen.getByText('Tags')).toBeDefined();
  expect(screen.getByText('Home')).toBeDefined();
  expect(screen.getByText('Menus')).toBeDefined();
});

test('highlights active navigation item', () => {
  mockPathname.mockReturnValue('/admin/posts');
  render(<Sidebar />);

  const postsLink = screen.getByText('Publicações');
  expect(postsLink.className).toContain('bg-blue-600');

  const dashboardLink = screen.getByText('Dashboard');
  expect(dashboardLink.className).not.toContain('bg-blue-600');
});

test('has correct href attributes', () => {
  render(<Sidebar />);

  expect(screen.getByText('Dashboard').closest('a')?.getAttribute('href')).toBe('/admin');
  expect(screen.getByText('Publicações').closest('a')?.getAttribute('href')).toBe('/admin/posts');
  expect(screen.getByText('Mídia').closest('a')?.getAttribute('href')).toBe('/admin/media');
  expect(screen.getByText('Categorias').closest('a')?.getAttribute('href')).toBe('/admin/categories');
});

test('mobile menu toggle works', () => {
  const { container } = render(<Sidebar />);

  const toggleButton = screen.getByLabelText('Toggle menu');
  expect(toggleButton).toBeDefined();

  // Sidebar should be hidden on mobile initially (translated off screen)
  const sidebar = container.querySelector('.w-64');
  expect(sidebar?.className).toContain('-translate-x-full');

  // Click toggle — sidebar should now be visible
  fireEvent.click(toggleButton);

  const sidebarAfter = container.querySelector('.w-64');
  expect(sidebarAfter?.className).toContain('translate-x-0');
  expect(sidebarAfter?.className).not.toContain('-translate-x-full');
});
