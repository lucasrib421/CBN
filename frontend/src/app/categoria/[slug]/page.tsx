import type { Metadata } from 'next';
import { fetchAPI } from '@/lib/api';
import type { Category, PaginatedResponse, PostSummary } from '@/types';
import PostCard from '@/components/PostCard';
import Link from 'next/link';

export const dynamic = 'force-dynamic';

interface PageProps {
  params: Promise<{ slug: string }>;
}

async function getCategories(): Promise<Category[]> {
  try {
    return await fetchAPI<Category[]>('/categories/');
  } catch {
    return [];
  }
}

async function getPostsByCategory(slug: string): Promise<PaginatedResponse<PostSummary>> {
  try {
    return await fetchAPI<PaginatedResponse<PostSummary>>(`/posts/?category=${slug}`);
  } catch {
    return { count: 0, next: null, previous: null, results: [] };
  }
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const categories = await getCategories();
  const category = categories.find((c) => c.slug === slug);

  return {
    title: category ? category.name : 'Categoria',
    description: category
      ? `Notícias sobre ${category.name} no CBN`
      : 'Notícias por categoria',
    openGraph: {
      title: category ? `${category.name} | CBN` : 'Categoria | CBN',
      description: category
        ? `Acompanhe as últimas notícias sobre ${category.name}`
        : 'Notícias por categoria',
      locale: 'pt_BR',
      type: 'website',
    },
  };
}

export default async function CategoryPage({ params }: PageProps) {
  const { slug } = await params;
  const [categories, postsData] = await Promise.all([
    getCategories(),
    getPostsByCategory(slug),
  ]);

  const category = categories.find((c) => c.slug === slug);
  const categoryName = category?.name || slug;
  const categoryColor = category?.color || '#DC2626';

  return (
    <div>
      {/* Category header */}
      <div className="mb-8 pb-6 border-b border-gray-200">
        <div className="flex items-center gap-3 mb-2">
          <span
            className="w-4 h-4 rounded-full inline-block"
            style={{ backgroundColor: categoryColor }}
          />
          <h1 className="text-3xl font-black text-gray-900 uppercase tracking-tight">
            {categoryName}
          </h1>
        </div>
        <p className="text-gray-500">
          {postsData.count} {postsData.count === 1 ? 'notícia encontrada' : 'notícias encontradas'}
        </p>
      </div>

      {/* Posts grid */}
      {postsData.results.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {postsData.results.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <p className="text-gray-500 text-lg mb-4">Nenhuma notícia nesta categoria.</p>
          <Link href="/" className="text-red-600 hover:text-red-700 font-medium transition-colors">
            &larr; Voltar para a Home
          </Link>
        </div>
      )}
    </div>
  );
}
