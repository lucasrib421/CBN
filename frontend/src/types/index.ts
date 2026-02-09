export interface Media {
  id: number;
  title: string;
  file: string;
  alt_text?: string;
  image_type: string;
}

export interface Author {
  id: string; // UUID
  name: string;
  bio?: string;
  avatar?: Media;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  color?: string;
}

export interface Tag {
  id: number;
  name: string;
  slug: string;
}

export interface PostSummary {
  id: number;
  title: string;
  subtitle: string;
  slug: string;
  cover_image?: Media;
  author: Author;
  categories: Category[];
  published_at: string | null;
  reading_time: number | null;
  created_at: string;
}

export interface PostDetail extends PostSummary {
  content: string;
  tags: Tag[];
  updated_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface HomeSectionItem {
  id: number;
  order: number;
  post: PostSummary;
}

export interface HomeSection {
  id: number;
  title: string;
  section_type: string;
  order: number;
  items: HomeSectionItem[];
}

export interface MenuItem {
  id: number;
  label: string;
  url: string;
  target?: string;
  order: number;
  children?: MenuItem[];
}

export interface Menu {
  id: number;
  title: string;
  slug: string;
  items: MenuItem[];
}
