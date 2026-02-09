import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import Image from 'next/image';
import Link from 'next/link';
import { fetchAPI } from '@/lib/api';
import type { PostDetail } from '@/types';

export const dynamic = 'force-dynamic';

interface PageProps {
  params: Promise<{ slug: string }>;
}

async function getPost(slug: string): Promise<PostDetail | null> {
  try {
    return await fetchAPI<PostDetail>(`/posts/${slug}/`);
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const post = await getPost(slug);

  if (!post) {
    return { title: 'Não encontrado' };
  }

  return {
    title: post.title,
    description: post.subtitle,
    openGraph: {
      title: post.title,
      description: post.subtitle,
      type: 'article',
      locale: 'pt_BR',
      ...(post.cover_image && {
        images: [{ url: post.cover_image.file, alt: post.cover_image.alt_text || post.title }],
      }),
      publishedTime: post.published_at || undefined,
      authors: [post.author.name],
    },
  };
}

export default async function PostPage({ params }: PageProps) {
  const { slug } = await params;
  const post = await getPost(slug);

  if (!post) {
    notFound();
  }

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'NewsArticle',
    headline: post.title,
    description: post.subtitle,
    ...(post.cover_image && { image: post.cover_image.file }),
    datePublished: post.published_at || post.created_at,
    dateModified: post.updated_at,
    author: {
      '@type': 'Person',
      name: post.author.name,
    },
    publisher: {
      '@type': 'Organization',
      name: 'CBN - Corrupção Brasileira News',
    },
  };

  return (
    <article className="max-w-3xl mx-auto">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      {/* Categories */}
      <div className="flex flex-wrap gap-2 mb-4">
        {post.categories.map((cat) => (
          <Link
            key={cat.id}
            href={`/categoria/${cat.slug}`}
            className="text-xs font-semibold px-2 py-1 bg-red-600 text-white rounded uppercase tracking-wider hover:bg-red-700 transition-colors"
          >
            {cat.name}
          </Link>
        ))}
      </div>

      {/* Title */}
      <h1 className="text-4xl font-black text-gray-900 leading-tight mb-3">
        {post.title}
      </h1>

      {/* Subtitle */}
      <p className="text-xl text-gray-600 mb-6">{post.subtitle}</p>

      {/* Author + Date */}
      <div className="flex items-center gap-4 text-sm text-gray-500 mb-8 pb-6 border-b border-gray-200">
        {post.author.avatar && (
          <Image
            src={post.author.avatar.file}
            alt={post.author.name}
            width={40}
            height={40}
            className="rounded-full object-cover"
          />
        )}
        <div>
          <span className="font-semibold text-gray-900">{post.author.name}</span>
          {post.published_at && (
            <time dateTime={post.published_at} className="block text-gray-500">
              {new Date(post.published_at).toLocaleDateString('pt-BR', {
                day: '2-digit',
                month: 'long',
                year: 'numeric',
              })}
            </time>
          )}
        </div>
        {post.reading_time && (
          <span className="ml-auto text-gray-400">{post.reading_time} min de leitura</span>
        )}
      </div>

      {/* Cover Image */}
      {post.cover_image && (
        <div className="relative aspect-video w-full mb-8 rounded-lg overflow-hidden bg-gray-100">
          <Image
            src={post.cover_image.file}
            alt={post.cover_image.alt_text || post.title}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, 768px"
            priority
          />
        </div>
      )}

      {/* Content */}
      <div
        className="prose prose-lg max-w-none prose-headings:text-gray-900 prose-a:text-red-600"
        dangerouslySetInnerHTML={{ __html: post.content }}
      />

      {/* Tags */}
      {post.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-10 pt-6 border-t border-gray-200">
          {post.tags.map((tag) => (
            <span
              key={tag.id}
              className="text-xs font-medium px-3 py-1 bg-gray-100 text-gray-600 rounded-full"
            >
              #{tag.name}
            </span>
          ))}
        </div>
      )}

      {/* Back link */}
      <div className="mt-10">
        <Link href="/" className="text-red-600 hover:text-red-700 font-medium transition-colors">
          &larr; Voltar para a Home
        </Link>
      </div>
    </article>
  );
}
