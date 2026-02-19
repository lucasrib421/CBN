import { redirect } from 'next/navigation'
import { auth } from '@/auth'
import { fetchAdminAPI } from '@/lib/admin-api'
import { PaginatedResponse, AdminPost, Category, Media } from '@/types'

export default async function DashboardPage() {
  const session = await auth()
  if (!session) {
    redirect('/api/auth/signin?callbackUrl=/admin')
  }

  let posts: PaginatedResponse<AdminPost>
  let categories: PaginatedResponse<Category>
  let media: PaginatedResponse<Media>
  let recentPosts: PaginatedResponse<AdminPost>

  try {
    ;[posts, categories, media] = await Promise.all([
      fetchAdminAPI<PaginatedResponse<AdminPost>>('/posts/'),
      fetchAdminAPI<PaginatedResponse<Category>>('/categories/'),
      fetchAdminAPI<PaginatedResponse<Media>>('/media/'),
    ])
    recentPosts = await fetchAdminAPI<PaginatedResponse<AdminPost>>('/posts/?ordering=-created_at')
  } catch {
    redirect('/api/auth/signin?callbackUrl=/admin')
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Painel de Controle</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 font-medium">Publicações</h3>
          <p className="text-3xl font-bold mt-2">{posts.count}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 font-medium">Categorias</h3>
          <p className="text-3xl font-bold mt-2">{categories.count}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 font-medium">Mídia</h3>
          <p className="text-3xl font-bold mt-2">{media.count}</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="font-bold text-lg">Publicações Recentes</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {recentPosts.results.map((post) => (
            <div key={post.id} className="p-6 hover:bg-gray-50">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-medium text-gray-900">{post.title}</h4>
                  <p className="text-sm text-gray-500 mt-1">
                    {new Date(post.created_at).toLocaleDateString('pt-BR')} • {post.status}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
