'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'

const navItems = [
  { name: 'Dashboard', href: '/admin' },
  { name: 'Publicações', href: '/admin/posts' },
  { name: 'Mídia', href: '/admin/media' },
  { name: 'Categorias', href: '/admin/categories' },
  { name: 'Tags', href: '/admin/tags' },
  { name: 'Home', href: '/admin/home-sections' },
  { name: 'Menus', href: '/admin/menus' },
]

export default function Sidebar() {
  const pathname = usePathname()
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <button
        type="button"
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-gray-900 text-white rounded cursor-pointer"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle menu"
      >
        Menu
      </button>

      <div
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-gray-900 text-white transform transition-transform duration-200 ease-in-out md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-6 font-bold text-xl border-b border-gray-800">
          CBN Admin
        </div>
        <nav className="mt-6 flex flex-col gap-1 px-4">
          {navItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-4 py-3 rounded transition-colors block ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`}
                onClick={() => setIsOpen(false)}
              >
                {item.name}
              </Link>
            )
          })}
        </nav>
      </div>

      {isOpen && (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-black/50 md:hidden w-full h-full cursor-default border-none block"
          onClick={() => setIsOpen(false)}
          aria-label="Close menu"
        />
      )}
    </>
  )
}
