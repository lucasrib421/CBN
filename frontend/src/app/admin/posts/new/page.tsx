'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { fetchAdminAPIClient } from '@/lib/admin-api'
import { Category, Tag, Media, PaginatedResponse } from '@/types'

const schema = z.object({
  title: z.string().min(3, 'O título deve ter pelo menos 3 caracteres'),
  subtitle: z.string().optional(),
  slug: z.string().min(3, 'O slug é obrigatório'),
  content: z.string().min(10, 'O conteúdo deve ter pelo menos 10 caracteres'),
  status: z.enum(['DRAFT', 'PUBLISHED', 'ARCHIVED']),
  categories: z.array(z.number()).min(1, 'Selecione pelo menos uma categoria'),
  tags: z.array(z.number()).optional(),
  cover_image: z.string().optional().nullable(), // Form uses string (ID), API expects number | null
  published_at: z.string().optional().nullable(),
  author: z.string().uuid('ID do autor inválido'),
})

type FormData = z.infer<typeof schema>

function generateSlug(title: string): string {
  return title
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

export default function NewPostPage() {
  const router = useRouter()
  const { data: session } = useSession()
  const [categories, setCategories] = useState<Category[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [mediaList, setMediaList] = useState<Media[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      status: 'DRAFT',
      categories: [],
      tags: [],
    },
  })

  const title = watch('title')
  const status = watch('status')

  // Auto-generate slug from title
  useEffect(() => {
    if (title) {
      setValue('slug', generateSlug(title))
    }
  }, [title, setValue])

  // Fetch dependencies
  useEffect(() => {
    async function loadData() {
      if (!session?.accessToken) return

      try {
        const [catsRes, tagsRes, mediaRes] = await Promise.all([
          fetchAdminAPIClient<PaginatedResponse<Category>>('/categories/', session.accessToken),
          fetchAdminAPIClient<PaginatedResponse<Tag>>('/tags/', session.accessToken),
          fetchAdminAPIClient<PaginatedResponse<Media>>('/media/', session.accessToken),
        ])
        setCategories(catsRes.results)
        setTags(tagsRes.results)
        setMediaList(mediaRes.results)
      } catch (err) {
        console.error('Failed to load form data:', err)
      }
    }
    loadData()
  }, [session])

  const onSubmit = async (data: FormData) => {
    if (!session?.accessToken) return
    setIsLoading(true)
    setSubmitError(null)

    try {
      // Transform form data for API
      const apiData = {
        ...data,
        cover_image: data.cover_image ? parseInt(data.cover_image) : null,
        tags: data.tags || [],
      }

      await fetchAdminAPIClient('/posts/', session.accessToken, {
        method: 'POST',
        body: JSON.stringify(apiData),
      })

      router.push('/admin/posts')
      router.refresh()
    } catch (err: any) {
      setSubmitError(err.message || 'Erro ao criar publicação')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Nova Publicação</h1>

      {submitError && (
        <div className="bg-red-50 text-red-600 p-4 rounded mb-6">
          {submitError}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 bg-white p-6 rounded shadow">
        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700">Título</label>
          <input
            id="title"
            {...register('title')}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
          />
          {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title.message}</p>}
        </div>

        {/* Subtitle */}
        <div>
          <label htmlFor="subtitle" className="block text-sm font-medium text-gray-700">Subtítulo</label>
          <input
            id="subtitle"
            {...register('subtitle')}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
          />
        </div>

        {/* Slug */}
        <div>
          <label htmlFor="slug" className="block text-sm font-medium text-gray-700">Slug</label>
          <input
            id="slug"
            {...register('slug')}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2 bg-gray-50"
          />
          {errors.slug && <p className="text-red-500 text-sm mt-1">{errors.slug.message}</p>}
        </div>

        {/* Content */}
        <div>
          <label htmlFor="content" className="block text-sm font-medium text-gray-700">Conteúdo</label>
          <textarea
            id="content"
            {...register('content')}
            rows={10}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
          />
          {errors.content && <p className="text-red-500 text-sm mt-1">{errors.content.message}</p>}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Status */}
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
            <select
              id="status"
              {...register('status')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
            >
              <option value="DRAFT">Rascunho</option>
              <option value="PUBLISHED">Publicado</option>
              <option value="ARCHIVED">Arquivado</option>
            </select>
          </div>

          {/* Published At */}
          {status === 'PUBLISHED' && (
            <div>
              <label htmlFor="published_at" className="block text-sm font-medium text-gray-700">Data de Publicação</label>
              <input
                id="published_at"
                type="datetime-local"
                {...register('published_at')}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
              />
            </div>
          )}
        </div>

        {/* Author */}
        <div>
          <label htmlFor="author" className="block text-sm font-medium text-gray-700">ID do Autor (UUID)</label>
          <input
            id="author"
            {...register('author')}
            placeholder="uuid-do-autor"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
          />
          {errors.author && <p className="text-red-500 text-sm mt-1">{errors.author.message}</p>}
        </div>

        {/* Categories */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Categorias</label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 border p-4 rounded max-h-48 overflow-y-auto">
            {categories.map((cat) => (
              <div key={cat.id} className="flex items-center">
                <input
                  id={`category-${cat.id}`}
                  type="checkbox"
                  value={cat.id}
                  {...register('categories', { valueAsNumber: true })}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor={`category-${cat.id}`} className="ml-2 block text-sm text-gray-900">{cat.name}</label>
              </div>
            ))}
          </div>
          {errors.categories && <p className="text-red-500 text-sm mt-1">{errors.categories.message}</p>}
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Tags</label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 border p-4 rounded max-h-48 overflow-y-auto">
            {tags.map((tag) => (
              <div key={tag.id} className="flex items-center">
                <input
                  id={`tag-${tag.id}`}
                  type="checkbox"
                  value={tag.id}
                  {...register('tags', { valueAsNumber: true })}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor={`tag-${tag.id}`} className="ml-2 block text-sm text-gray-900">{tag.name}</label>
              </div>
            ))}
          </div>
        </div>

        {/* Cover Image */}
        <div>
          <label htmlFor="cover_image" className="block text-sm font-medium text-gray-700">Imagem de Capa</label>
          <select
            id="cover_image"
            {...register('cover_image')}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
          >
            <option value="">Selecione uma imagem...</option>
            {mediaList.map((media) => (
              <option key={media.id} value={media.id}>
                {media.title} ({media.image_type})
              </option>
            ))}
          </select>
        </div>

        <div className="flex justify-end pt-6">
          <button
            type="button"
            onClick={() => router.back()}
            className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none mr-3"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isLoading ? 'Salvando...' : 'Salvar Publicação'}
          </button>
        </div>
      </form>
    </div>
  )
}
