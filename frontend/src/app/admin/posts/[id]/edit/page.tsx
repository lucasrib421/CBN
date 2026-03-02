'use client'

import { useState, useEffect } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { fetchAdminAPIClient } from '@/lib/admin-api'
import PostRichTextEditor from '@/components/admin/posts/PostRichTextEditor'
import { normalizeRelatedIds } from '@/components/admin/posts/post-form-normalizers'
import { PostFormData, postFormSchema } from '@/components/admin/posts/post-form-schema'
import { buildStatusOptions, STATUS_LABELS } from '@/components/admin/posts/workflow'
import { useStableAccessToken } from '@/lib/use-stable-access-token'
import {
  AdminPost,
  AvailableTransitionsResponse,
  Category,
  Media,
  PaginatedResponse,
  Tag,
} from '@/types'

export default function EditPostPage(props: { params: Promise<{ id: string }> }) {
  const router = useRouter()
  const { data: session, status: authStatus } = useSession()
  const resolveAccessToken = useStableAccessToken(session?.accessToken)
  const [categories, setCategories] = useState<Category[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [mediaList, setMediaList] = useState<Media[]>([])
  const [statusOptions, setStatusOptions] = useState(
    buildStatusOptions('DRAFT', ['REVIEW', 'PUBLISHED', 'ARCHIVED']),
  )
  const [isLoading, setIsLoading] = useState(true)
  const [submitError, setSubmitError] = useState<string | null>(null)
  
  // Unwrap params
  const [postId, setPostId] = useState<string | null>(null)

  useEffect(() => {
    props.params.then(p => setPostId(p.id))
  }, [props.params])

  const {
    register,
    control,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
  } = useForm<PostFormData>({
    resolver: zodResolver(postFormSchema),
    defaultValues: {
      content: '<p></p>',
      status: 'DRAFT',
      categories: [],
      tags: [],
    },
  })

  const postStatus = watch('status')

  // Fetch data
  useEffect(() => {
    async function loadData() {
      if (!postId || authStatus !== 'authenticated' || !session?.accessToken) return

      try {
        const [catsRes, tagsRes, mediaRes, postRes] = await Promise.all([
          fetchAdminAPIClient<PaginatedResponse<Category>>('/categories/', session.accessToken),
          fetchAdminAPIClient<PaginatedResponse<Tag>>('/tags/', session.accessToken),
          fetchAdminAPIClient<PaginatedResponse<Media>>('/media/', session.accessToken),
          fetchAdminAPIClient<AdminPost>(`/posts/${postId}/`, session.accessToken),
        ])
        const transitionsRes = await fetchAdminAPIClient<AvailableTransitionsResponse>(
          `/posts/available-transitions/?status=${postRes.status}`,
          session.accessToken,
        )
        setCategories(catsRes.results)
        setTags(tagsRes.results)
        setMediaList(mediaRes.results)
        setStatusOptions(
          buildStatusOptions(postRes.status, transitionsRes.allowed_transitions, transitionsRes.labels),
        )

        reset({
          title: postRes.title,
          subtitle: postRes.subtitle || '',
          slug: postRes.slug,
          content: postRes.content || '<p></p>',
          status: postRes.status,
          published_at: postRes.published_at ? postRes.published_at.slice(0, 16) : null,
          categories: postRes.categories?.map((c) => c.id) || [],
          tags: postRes.tags?.map((t) => t.id) || [],
          cover_image: postRes.cover_image ? String(postRes.cover_image.id) : null,
        })
      } catch (err: any) {
        console.error('Failed to load data:', err)
        setSubmitError(err.message || 'Erro ao carregar dados')
      } finally {
        setIsLoading(false)
      }
    }
    loadData()
  }, [authStatus, postId, reset, session?.accessToken])

  const onSubmit = async (data: PostFormData) => {
    if (!postId) return
    setIsLoading(true)
    setSubmitError(null)

    try {
      const accessToken = await resolveAccessToken()
      const apiData = {
        ...data,
        categories: normalizeRelatedIds(data.categories),
        cover_image: data.cover_image ? parseInt(data.cover_image) : null,
        tags: normalizeRelatedIds(data.tags),
      }

      await fetchAdminAPIClient(`/posts/${postId}/`, accessToken, {
        method: 'PUT',
        body: JSON.stringify(apiData),
      })

      router.push('/admin/posts')
      router.refresh()
    } catch (err: any) {
      setSubmitError(err.message || 'Erro ao atualizar publicação')
      setIsLoading(false)
    }
  }

  if (isLoading && !categories.length) {
    return <div className="p-8 text-center text-gray-500">Carregando...</div>
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Editar Publicação</h1>
      </div>

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
          <label className="block text-sm font-medium text-gray-700">Conteúdo</label>
          <div className="mt-1">
            <Controller
              control={control}
              name="content"
              render={({ field }) => (
                <PostRichTextEditor
                  value={field.value}
                  onChange={field.onChange}
                  onBlur={field.onBlur}
                  error={errors.content?.message}
                />
              )}
            />
          </div>
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
              {statusOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label || STATUS_LABELS[option.value]}
                </option>
              ))}
            </select>
          </div>

          {/* Published At */}
          {postStatus === 'PUBLISHED' && (
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
            {isLoading ? 'Salvando...' : 'Salvar Alterações'}
          </button>
        </div>
      </form>
    </div>
  )
}
