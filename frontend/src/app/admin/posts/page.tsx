import { auth } from '@/auth'
import { fetchAdminAPI } from '@/lib/admin-api'
import { AdminPost, PaginatedResponse } from '@/types'
import Link from 'next/link'
import { redirect } from 'next/navigation'

export default async function PostsPage(props: {
  searchParams: Promise<{ page?: string }>
}) {
  const searchParams = await props.searchParams
  const session = await auth()
  if (!session) {
    redirect('/api/auth/signin?callbackUrl=/admin/posts')
  }

  const page = searchParams.page || '1'
  let posts: PaginatedResponse<AdminPost>

  try {
    posts = await fetchAdminAPI<PaginatedResponse<AdminPost>>(
      `/posts/?page=${page}&ordering=-created_at`
    )
  } catch (error) {
    console.error('Failed to fetch posts:', error)
    return (
      <div className="p-4 text-red-500 bg-red-50 rounded">
        Erro ao carregar publicações. Por favor, tente novamente.
      </div>
    )
  }

  const totalPages = Math.ceil(posts.count / 10) // Assuming default page size is 10
  const currentPage = parseInt(page)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Publicações</h1>
        <Link
          href="/admin/posts/new"
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors"
        >
          Nova Publicação
        </Link>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Título
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Autor
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Data
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ações
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {posts.results.map((post) => (
              <tr key={post.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900 truncate max-w-xs">
                    {post.title}
                  </div>
                  <div className="text-sm text-gray-500 truncate max-w-xs">
                    {post.subtitle}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      post.status === 'PUBLISHED'
                        ? 'bg-green-100 text-green-800'
                        : post.status === 'DRAFT'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {post.status === 'PUBLISHED'
                      ? 'Publicado'
                      : post.status === 'DRAFT'
                      ? 'Rascunho'
                      : 'Arquivado'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {post.author_name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {post.published_at
                    ? new Date(post.published_at).toLocaleDateString('pt-BR')
                    : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link
                    href={`/admin/posts/${post.id}/edit`}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    Editar
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex justify-between items-center bg-white px-4 py-3 border-t border-gray-200 sm:px-6 rounded-lg shadow">
        <div className="flex-1 flex justify-between sm:hidden">
          <Link
            href={
              posts.previous
                ? `/admin/posts?page=${currentPage - 1}`
                : '#'
            }
            className={`relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 ${
              !posts.previous ? 'opacity-50 pointer-events-none' : ''
            }`}
          >
            Anterior
          </Link>
          <Link
            href={
              posts.next
                ? `/admin/posts?page=${currentPage + 1}`
                : '#'
            }
            className={`ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 ${
              !posts.next ? 'opacity-50 pointer-events-none' : ''
            }`}
          >
            Próximo
          </Link>
        </div>
        <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p className="text-sm text-gray-700">
              Mostrando <span className="font-medium">{(currentPage - 1) * 10 + 1}</span> a{' '}
              <span className="font-medium">
                {Math.min(currentPage * 10, posts.count)}
              </span>{' '}
              de <span className="font-medium">{posts.count}</span> resultados
            </p>
          </div>
          <div>
            <nav
              className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px"
              aria-label="Pagination"
            >
              <Link
                href={
                  posts.previous
                    ? `/admin/posts?page=${currentPage - 1}`
                    : '#'
                }
                className={`relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 ${
                  !posts.previous ? 'opacity-50 pointer-events-none' : ''
                }`}
              >
                <span className="sr-only">Anterior</span>
                Anterior
              </Link>
              <Link
                href={
                  posts.next
                    ? `/admin/posts?page=${currentPage + 1}`
                    : '#'
                }
                className={`relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 ${
                  !posts.next ? 'opacity-50 pointer-events-none' : ''
                }`}
              >
                <span className="sr-only">Próximo</span>
                Próximo
              </Link>
            </nav>
          </div>
        </div>
      </div>
    </div>
  )
}
