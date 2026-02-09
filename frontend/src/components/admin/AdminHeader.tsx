'use client'

import { useSession, signOut } from 'next-auth/react'

export default function AdminHeader() {
  const { data: session } = useSession()

  return (
    <header className="bg-white shadow h-16 flex items-center justify-end px-8 md:ml-64">
      <div className="flex items-center gap-4">
        <span className="text-gray-700 font-medium">
          {session?.user?.name || session?.user?.email || 'Admin'}
        </span>
        <button
          type="button"
          onClick={() => signOut({ callbackUrl: '/' })}
          className="text-sm text-red-600 hover:text-red-800 font-medium cursor-pointer"
        >
          Sair
        </button>
      </div>
    </header>
  )
}
