import { HomeSection as HomeSectionType } from '@/types';
import PostCard from './PostCard';

export default function HomeSection({ section }: { section: HomeSectionType }) {
  if (!section.items || section.items.length === 0) return null;

  return (
    <section className="py-8 border-b border-gray-100 last:border-0">
      <div className="container mx-auto px-4">
        <div className="flex items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900 uppercase tracking-tight border-l-4 border-red-600 pl-3">
                {section.title}
            </h2>
        </div>
        
        {section.section_type === 'HIGHLIGHTS' ? (
           <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
             {section.items.slice(0, 1).map((item) => (
                <div key={item.id} className="md:col-span-8">
                   <PostCard post={item.post} className="h-full" priority={true} />
                </div>
             ))}
             <div className="md:col-span-4 flex flex-col gap-6">
                {section.items.slice(1, 3).map((item) => (
                   <PostCard key={item.id} post={item.post} className="h-full" />
                ))}
             </div>
           </div>
        ) : (
           <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {section.items.map((item) => (
                 <PostCard key={item.id} post={item.post} />
              ))}
           </div>
        )}
      </div>
    </section>
  );
}
