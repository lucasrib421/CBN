'use client'

import { useState, useEffect, useCallback } from 'react'
import { useSession } from 'next-auth/react'
import { fetchAdminAPIClient } from '@/lib/admin-api'
import { AdminHomeSection, AdminHomeSectionItem, AdminPost, PaginatedResponse } from '@/types'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

// --- Section Form ---
const sectionSchema = z.object({
  title: z.string().min(1, 'Título é obrigatório'),
  section_type: z.string().min(1, 'Tipo é obrigatório'),
  order: z.number().int(),
  is_active: z.boolean(),
})
type SectionFormData = z.infer<typeof sectionSchema>

// --- Item Form ---
const itemSchema = z.object({
  post: z.number().min(1, 'Selecione uma publicação'),
  order: z.number().int(),
})
type ItemFormData = z.infer<typeof itemSchema>

export default function HomeSectionsPage() {
  const { data: session } = useSession()
  const [sections, setSections] = useState<AdminHomeSection[]>([])
  const [itemsBySection, setItemsBySection] = useState<Record<number, AdminHomeSectionItem[]>>({})
  const [posts, setPosts] = useState<AdminPost[]>([])
  const [expandedSectionId, setExpandedSectionId] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isCreatingSection, setIsCreatingSection] = useState(false)
  
  // Fetch Sections
  const fetchSections = useCallback(async () => {
    if (!session?.accessToken) return
    try {
      const res = await fetchAdminAPIClient<PaginatedResponse<AdminHomeSection>>(
        '/home-sections/?ordering=order',
        session.accessToken
      )
      setSections(res.results)
    } catch (err) {
      console.error('Error fetching sections', err)
    } finally {
      setIsLoading(false)
    }
  }, [session])

  // Fetch Posts (for selection)
  const fetchPosts = useCallback(async () => {
    if (!session?.accessToken) return
    try {
      // Get 100 most recent published posts
      const res = await fetchAdminAPIClient<PaginatedResponse<AdminPost>>(
        '/posts/?status=PUBLISHED&page_size=100',
        session.accessToken
      )
      setPosts(res.results)
    } catch (err) {
      console.error('Error fetching posts', err)
    }
  }, [session])

  useEffect(() => {
    if (session?.accessToken) {
      fetchSections()
      fetchPosts()
    }
  }, [session, fetchSections, fetchPosts])

  // Fetch Items for a Section
  const fetchItems = async (sectionId: number) => {
    if (!session?.accessToken) return
    try {
      const res = await fetchAdminAPIClient<PaginatedResponse<AdminHomeSectionItem>>(
        `/home-section-items/?section=${sectionId}&ordering=order`,
        session.accessToken
      )
      setItemsBySection(prev => ({ ...prev, [sectionId]: res.results }))
    } catch (err) {
      console.error('Error fetching items', err)
    }
  }

  const toggleSection = (sectionId: number) => {
    if (expandedSectionId === sectionId) {
      setExpandedSectionId(null)
    } else {
      setExpandedSectionId(sectionId)
      fetchItems(sectionId)
    }
  }

  const createSection = async (data: SectionFormData) => {
    if (!session?.accessToken) return
    await fetchAdminAPIClient('/home-sections/', session.accessToken, {
      method: 'POST',
      body: JSON.stringify(data),
    })
    setIsCreatingSection(false)
    fetchSections()
  }

  const deleteSection = async (id: number) => {
    if (!confirm('Excluir seção?')) return
    if (!session?.accessToken) return
    await fetchAdminAPIClient(`/home-sections/${id}/`, session.accessToken, {
      method: 'DELETE',
    })
    fetchSections()
  }

  const addItem = async (sectionId: number, data: ItemFormData) => {
    if (!session?.accessToken) return
    await fetchAdminAPIClient('/home-section-items/', session.accessToken, {
      method: 'POST',
      body: JSON.stringify({ ...data, section: sectionId }),
    })
    fetchItems(sectionId)
  }

  const deleteItem = async (itemId: number, sectionId: number) => {
    if (!confirm('Remover item?')) return
    if (!session?.accessToken) return
    await fetchAdminAPIClient(`/home-section-items/${itemId}/`, session.accessToken, {
      method: 'DELETE',
    })
    fetchItems(sectionId)
  }
  
  // Reorder Item (simple swap or update order)
  // For simplicity, I'll just rely on editing order or delete/re-add for now, 
  // or add Up/Down buttons that swap orders.
  // Implementing Up/Down:
  const moveItem = async (item: AdminHomeSectionItem, direction: 'up' | 'down', allItems: AdminHomeSectionItem[]) => {
    if (!session?.accessToken) return
    const index = allItems.findIndex(i => i.id === item.id)
    if (index === -1) return
    
    const targetIndex = direction === 'up' ? index - 1 : index + 1
    if (targetIndex < 0 || targetIndex >= allItems.length) return

    const targetItem = allItems[targetIndex]
    
    // Swap orders
    // We update both items
    // This is naive concurrency-wise but fine for admin
    await Promise.all([
      fetchAdminAPIClient(`/home-section-items/${item.id}/`, session.accessToken, {
        method: 'PATCH',
        body: JSON.stringify({ order: targetItem.order }),
      }),
      fetchAdminAPIClient(`/home-section-items/${targetItem.id}/`, session.accessToken, {
        method: 'PATCH',
        body: JSON.stringify({ order: item.order }),
      })
    ])
    fetchItems(item.section)
  }

  if (isLoading) return <div className="p-8 text-center text-gray-500">Carregando...</div>

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Seções da Home</h1>
        <button
          type="button"
          onClick={() => setIsCreatingSection(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors"
        >
          Nova Seção
        </button>
      </div>

      {isCreatingSection && (
        <div className="bg-white p-4 rounded shadow mb-4 border-l-4 border-blue-500">
           <SectionForm onSubmit={createSection} onCancel={() => setIsCreatingSection(false)} />
        </div>
      )}

      <div className="space-y-4">
        {sections.map((section) => (
          <div key={section.id} className="bg-white shadow rounded-lg overflow-hidden">
            <div className="p-4 flex items-center justify-between bg-gray-50 border-b">
              <div className="flex items-center gap-4">
                <button
                  type="button"
                  onClick={() => toggleSection(section.id)}
                  className="text-gray-500 hover:text-gray-700 focus:outline-none"
                  aria-label={expandedSectionId === section.id ? "Recolher seção" : "Expandir seção"}
                >
                  {expandedSectionId === section.id ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                  )}
                </button>
                <div>
                  <h3 className="text-lg font-medium text-gray-900">{section.title}</h3>
                  <span className="text-xs text-gray-500">Tipo: {section.section_type} | Ordem: {section.order}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                 <button
                    type="button"
                    onClick={() => deleteSection(section.id)}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    Excluir
                  </button>
              </div>
            </div>
            
            {expandedSectionId === section.id && (
              <div className="p-4 bg-white">
                <h4 className="font-medium mb-3 text-sm text-gray-700">Itens da Seção</h4>
                
                <div className="space-y-2 mb-4">
                  {(itemsBySection[section.id] || []).map((item, idx, arr) => {
                    const post = posts.find(p => p.id === item.post)
                    return (
                      <div key={item.id} className="flex items-center justify-between p-2 bg-gray-50 rounded border border-gray-100">
                        <span className="truncate flex-1 font-medium text-sm text-gray-900">
                           {post ? post.title : `Post ID ${item.post}`}
                        </span>
                        <div className="flex items-center gap-2 ml-4">
                          <button
                            type="button"
                            onClick={() => moveItem(item, 'up', arr)}
                            disabled={idx === 0}
                            className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                            aria-label="Mover para cima"
                          >
                             ↑
                          </button>
                          <button
                            type="button"
                            onClick={() => moveItem(item, 'down', arr)}
                            disabled={idx === arr.length - 1}
                            className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                            aria-label="Mover para baixo"
                          >
                             ↓
                          </button>
                          <button
                            type="button"
                            onClick={() => deleteItem(item.id, section.id)}
                            className="text-red-500 hover:text-red-700 text-sm ml-2"
                          >
                            ×
                          </button>
                        </div>
                      </div>
                    )
                  })}
                  {(!itemsBySection[section.id] || itemsBySection[section.id].length === 0) && (
                    <p className="text-sm text-gray-400 italic">Nenhum item nesta seção.</p>
                  )}
                </div>

                <div className="mt-4 pt-4 border-t">
                  <ItemForm 
                    posts={posts} 
                    nextOrder={(itemsBySection[section.id]?.length || 0) + 1}
                    onSubmit={(data) => addItem(section.id, data)} 
                  />
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function SectionForm({ onSubmit, onCancel }: { onSubmit: (data: SectionFormData) => void, onCancel: () => void }) {
  const { register, handleSubmit, formState: { errors } } = useForm<SectionFormData>({
    resolver: zodResolver(sectionSchema),
    defaultValues: { is_active: true, order: 0 }
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="section-title" className="block text-sm font-medium text-gray-700">Título</label>
          <input id="section-title" {...register('title')} className="mt-1 block w-full rounded border-gray-300 p-2 border" />
          {errors.title && <p className="text-red-500 text-xs">{errors.title.message}</p>}
        </div>
        <div>
          <label htmlFor="section-type" className="block text-sm font-medium text-gray-700">Tipo</label>
          <select id="section-type" {...register('section_type')} className="mt-1 block w-full rounded border-gray-300 p-2 border">
            <option value="featured">Destaque</option>
            <option value="list">Lista</option>
            <option value="grid">Grid</option>
          </select>
        </div>
        <div>
           <label htmlFor="section-order" className="block text-sm font-medium text-gray-700">Ordem</label>
           <input id="section-order" type="number" {...register('order', { valueAsNumber: true })} className="mt-1 block w-full rounded border-gray-300 p-2 border" />
        </div>
        <div className="flex items-center mt-6">
           <input id="section-active" type="checkbox" {...register('is_active')} className="h-4 w-4 text-blue-600 rounded" />
           <label htmlFor="section-active" className="ml-2 block text-sm text-gray-900">Ativo</label>
        </div>
      </div>
      <div className="flex justify-end gap-2">
        <button type="button" onClick={onCancel} className="px-4 py-2 border rounded text-gray-600 hover:bg-gray-50">Cancelar</button>
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Salvar</button>
      </div>
    </form>
  )
}

function ItemForm({ posts, nextOrder, onSubmit }: { posts: AdminPost[], nextOrder: number, onSubmit: (data: ItemFormData) => void }) {
  const { register, handleSubmit, reset } = useForm<ItemFormData>({
    resolver: zodResolver(itemSchema),
    defaultValues: { order: nextOrder }
  })

  const handleFormSubmit = (data: ItemFormData) => {
    onSubmit(data)
    reset({ order: nextOrder + 1 })
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="flex gap-2 items-end">
       <div className="flex-1">
         <label htmlFor={`item-post-${nextOrder}`} className="block text-xs font-medium text-gray-500 mb-1">Adicionar Publicação</label>
         <select id={`item-post-${nextOrder}`} {...register('post', { valueAsNumber: true })} className="block w-full rounded border-gray-300 p-2 text-sm border">
            <option value="">Selecione...</option>
            {posts.map(post => (
              <option key={post.id} value={post.id}>{post.title} ({post.status})</option>
            ))}
         </select>
       </div>
       <div className="w-20">
         <label htmlFor={`item-order-${nextOrder}`} className="block text-xs font-medium text-gray-500 mb-1">Ordem</label>
         <input id={`item-order-${nextOrder}`} type="number" {...register('order', { valueAsNumber: true })} className="block w-full rounded border-gray-300 p-2 text-sm border" />
       </div>
       <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded text-sm hover:bg-green-700 mb-[1px]">Adicionar</button>
    </form>
  )
}
