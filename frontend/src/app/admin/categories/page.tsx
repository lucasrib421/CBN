'use client'

import { useState, useEffect, useCallback } from 'react'
import { useSession } from 'next-auth/react'
import { fetchAdminAPIClient } from '@/lib/admin-api'
import { Category, PaginatedResponse } from '@/types'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const schema = z.object({
  name: z.string().min(1, 'Nome é obrigatório'),
  slug: z.string().min(1, 'Slug é obrigatório'),
  color: z.string().regex(/^#[0-9A-F]{6}$/i, 'Cor inválida').optional().or(z.literal('')),
})

type FormData = z.infer<typeof schema>

function generateSlug(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

export default function CategoriesPage() {
  const { data: session } = useSession()
  const [categories, setCategories] = useState<Category[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const name = watch('name')

  // Auto-generate slug when creating
  useEffect(() => {
    if (isCreating && !editingId && name) {
      setValue('slug', generateSlug(name))
    }
  }, [name, isCreating, editingId, setValue])

  const fetchCategories = useCallback(async () => {
    if (!session?.accessToken) return
    try {
      const res = await fetchAdminAPIClient<PaginatedResponse<Category>>(
        '/categories/',
        session.accessToken
      )
      setCategories(res.results)
    } catch (err) {
      setError('Erro ao carregar categorias')
    } finally {
      setIsLoading(false)
    }
  }, [session])

  useEffect(() => {
    if (session?.accessToken) {
      fetchCategories()
    }
  }, [session, fetchCategories])

  function startCreate() {
    setIsCreating(true)
    setEditingId(null)
    reset({ name: '', slug: '', color: '#000000' })
  }

  function startEdit(category: Category) {
    setIsCreating(false)
    setEditingId(category.id)
    reset({
      name: category.name,
      slug: category.slug,
      color: category.color || '#000000',
    })
  }

  function cancel() {
    setIsCreating(false)
    setEditingId(null)
    reset()
  }

  async function onSubmit(data: FormData) {
    if (!session?.accessToken) return

    try {
      if (isCreating) {
        const newCat = await fetchAdminAPIClient<Category>('/categories/', session.accessToken, {
          method: 'POST',
          body: JSON.stringify(data),
        })
        setCategories([...categories, newCat])
      } else if (editingId) {
        const updatedCat = await fetchAdminAPIClient<Category>(
          `/categories/${editingId}/`,
          session.accessToken,
          {
            method: 'PUT',
            body: JSON.stringify(data),
          }
        )
        setCategories(categories.map((c) => (c.id === editingId ? updatedCat : c)))
      }
      cancel()
    } catch (err: any) {
      setError(err.message || 'Erro ao salvar categoria')
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('Tem certeza que deseja excluir esta categoria?')) return
    if (!session?.accessToken) return

    try {
      await fetchAdminAPIClient(`/categories/${id}/`, session.accessToken, {
        method: 'DELETE',
      })
      setCategories(categories.filter((c) => c.id !== id))
    } catch (err: any) {
      setError(err.message || 'Erro ao excluir categoria')
    }
  }

  if (isLoading) return <div className="p-8 text-center text-gray-500">Carregando...</div>

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Categorias</h1>
        <button
          type="button"
          onClick={startCreate}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors"
          disabled={isCreating || editingId !== null}
        >
          Nova Categoria
        </button>
      </div>

      {error && <div className="bg-red-50 text-red-600 p-4 rounded">{error}</div>}

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Cor
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nome
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Slug
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ações
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {isCreating && (
              <tr className="bg-blue-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <input
                    type="color"
                    {...register('color')}
                    className="h-8 w-8 rounded border border-gray-300 p-1"
                    aria-label="Cor da categoria"
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <input
                    {...register('name')}
                    placeholder="Nome"
                    className="w-full rounded border-gray-300 p-1 text-sm border"
                    aria-label="Nome da categoria"
                  />
                  {errors.name && <span className="text-xs text-red-500">{errors.name.message}</span>}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <input
                    {...register('slug')}
                    placeholder="slug"
                    className="w-full rounded border-gray-300 p-1 text-sm border bg-gray-100"
                    aria-label="Slug da categoria"
                  />
                  {errors.slug && <span className="text-xs text-red-500">{errors.slug.message}</span>}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    type="button"
                    onClick={handleSubmit(onSubmit)}
                    className="text-green-600 hover:text-green-900 mr-3"
                  >
                    Salvar
                  </button>
                  <button type="button" onClick={cancel} className="text-gray-600 hover:text-gray-900">
                    Cancelar
                  </button>
                </td>
              </tr>
            )}

            {categories.map((category) => {
              const isEditing = editingId === category.id
              return (
                <tr key={category.id} className={isEditing ? 'bg-blue-50' : ''}>
                  {isEditing ? (
                    <>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <input
                          type="color"
                          {...register('color')}
                          className="h-8 w-8 rounded border border-gray-300 p-1"
                          aria-label="Cor da categoria"
                        />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <input
                          {...register('name')}
                          className="w-full rounded border-gray-300 p-1 text-sm border"
                          aria-label="Nome da categoria"
                        />
                        {errors.name && (
                          <span className="text-xs text-red-500">{errors.name.message}</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <input
                          {...register('slug')}
                          className="w-full rounded border-gray-300 p-1 text-sm border bg-gray-100"
                          aria-label="Slug da categoria"
                        />
                        {errors.slug && (
                          <span className="text-xs text-red-500">{errors.slug.message}</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          type="button"
                          onClick={handleSubmit(onSubmit)}
                          className="text-green-600 hover:text-green-900 mr-3"
                        >
                          Salvar
                        </button>
                        <button type="button" onClick={cancel} className="text-gray-600 hover:text-gray-900">
                          Cancelar
                        </button>
                      </td>
                    </>
                  ) : (
                    <>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div
                          className="h-6 w-6 rounded-full border border-gray-200"
                          style={{ backgroundColor: category.color || '#cccccc' }}
                          title={category.color}
                        />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {category.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {category.slug}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          type="button"
                          onClick={() => startEdit(category)}
                          disabled={isCreating || editingId !== null}
                          className="text-blue-600 hover:text-blue-900 mr-3 disabled:opacity-50"
                        >
                          Editar
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(category.id)}
                          disabled={isCreating || editingId !== null}
                          className="text-red-600 hover:text-red-900 disabled:opacity-50"
                        >
                          Excluir
                        </button>
                      </td>
                    </>
                  )}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
