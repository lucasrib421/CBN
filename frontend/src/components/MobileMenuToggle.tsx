'use client';

import { useState } from 'react';
import Link from 'next/link';
import type { MenuItem } from '@/types';

export default function MobileMenuToggle({ items }: { items: MenuItem[] }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="md:hidden">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="text-white p-2"
        aria-label={open ? 'Fechar menu' : 'Abrir menu'}
        aria-expanded={open}
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {open ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>

      {open && (
        <nav className="absolute top-16 left-0 right-0 bg-black border-t border-gray-800 shadow-lg" aria-label="Menu mobile">
          <ul className="flex flex-col py-2">
            {items.map((item) => (
              <li key={item.id}>
                <Link
                  href={`/categoria${item.url}`}
                  onClick={() => setOpen(false)}
                  className="block px-6 py-3 text-sm font-bold uppercase tracking-wide text-white hover:bg-gray-900 hover:text-red-500 transition-colors"
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </div>
  );
}
