import Link from 'next/link';
import { PostSummary } from '@/types';
import Image from 'next/image';

interface PostCardProps {
  post: PostSummary;
  className?: string;
  priority?: boolean;
}

export default function PostCard({ post, className = '', priority = false }: PostCardProps) {
  return (
    <article className={`group flex flex-col h-full bg-white border border-gray-100 shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden rounded-lg ${className}`}>
      {post.cover_image && (
        <div className="relative aspect-video w-full overflow-hidden bg-gray-100">
           <Image 
              src={post.cover_image.file}
              alt={post.cover_image.alt_text || post.title}
              fill
              className="object-cover group-hover:scale-105 transition-transform duration-300"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              priority={priority}
            />
        </div>
      )}
      <div className="p-4 flex flex-col flex-grow">
        <div className="flex flex-wrap gap-2 mb-3">
            {post.categories.map((cat) => (
                <span key={cat.id} className="text-xs font-semibold px-2 py-1 bg-red-600 text-white rounded uppercase tracking-wider">
                    {cat.name}
                </span>
            ))}
        </div>
        <Link href={`/${post.slug}`} className="block mt-2">
            <h3 className="text-xl font-bold text-gray-900 group-hover:text-red-700 leading-tight mb-2">
                {post.title}
            </h3>
        </Link>
        <p className="text-gray-600 text-sm line-clamp-3 mb-4 flex-grow">
            {post.subtitle}
        </p>
        <div className="flex items-center justify-between text-xs text-gray-500 border-t pt-3 mt-auto">
            <span className="font-medium text-gray-900">{post.author.name}</span>
            {post.published_at && (
                <time dateTime={post.published_at}>
                    {new Date(post.published_at).toLocaleDateString('pt-BR', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric'
                    })}
                </time>
            )}
        </div>
      </div>
    </article>
  );
}
