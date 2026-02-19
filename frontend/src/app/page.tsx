import { fetchAPI } from '@/lib/api';
import type { HomeSection as HomeSectionType } from '@/types';
import HomeSection from '@/components/HomeSection';

export const dynamic = 'force-dynamic';

export default async function HomePage() {
  let sections: HomeSectionType[] = [];

  try {
    sections = await fetchAPI<HomeSectionType[]>('/home/');
  } catch {
    // API may be unavailable during build
  }

  if (sections.length === 0) {
    return (
      <div className="text-center py-20">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">CBN</h1>
        <p className="text-gray-500">Nenhuma notícia disponível no momento.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {sections.map((section) => (
        <HomeSection key={section.id} section={section} />
      ))}
    </div>
  );
}
