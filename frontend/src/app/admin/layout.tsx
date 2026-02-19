import AdminHeader from '@/components/admin/AdminHeader'
import Sidebar from '@/components/admin/Sidebar'
import AdminProviders from './providers'

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <AdminProviders>
      <div className="min-h-screen bg-gray-100">
        <Sidebar />
        <AdminHeader />
        <main className="md:ml-64 p-8">
          {children}
        </main>
      </div>
    </AdminProviders>
  )
}
