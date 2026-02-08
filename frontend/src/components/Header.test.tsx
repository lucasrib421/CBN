import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';

import { Header } from './Header';

vi.mock('../services/newsService', () => ({
  NewsService: {
    getMenus: vi.fn().mockResolvedValue([]),
  },
}));

describe('Header', () => {
  it('renders project title', () => {
    render(<Header />);

    expect(screen.getByText('Corrupção Brasileira News')).toBeInTheDocument();
  });
});
