import Link from 'next/link';
import Image from 'next/image';
import { fetchAPI } from '@/lib/api';
import type { Menu } from '@/types';
import MobileMenuToggle from './MobileMenuToggle';

export default async function Header() {
  let menuItems: Menu['items'] = [];

  try {
    const menus = await fetchAPI<Menu[]>('/menus/', { revalidate: 3600 });
    const mainMenu = menus.find((m) => m.slug === 'menu-principal');
    if (mainMenu) {
      menuItems = mainMenu.items;
    }
  } catch {
    // Menu may be unavailable during build
  }

  return (
    <header className="bg-black text-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
        <Link href="/" className="flex items-center gap-3 no-underline">
          <Image
            src="/images/CBN_LOGO.png"
            alt="Logo CBN"
            width={48}
            height={48}
            className="h-12 w-auto object-contain"
            priority
          />
          <span className="text-sm uppercase tracking-widest text-white/80 hidden sm:inline">
            Corrupção Brasileira News
          </span>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:block" aria-label="Menu principal">
          <ul className="flex gap-6">
            {menuItems.map((item) => (
              <li key={item.id}>
                <Link
                  href={`/categoria${item.url}`}
                  className="text-sm font-bold uppercase tracking-wide text-white hover:text-red-500 transition-colors"
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        {/* Mobile toggle */}
        <MobileMenuToggle items={menuItems} />
      </div>
    </header>
  );
}
