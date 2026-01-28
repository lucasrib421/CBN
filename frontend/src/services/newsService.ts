import { api } from './api';
import type{ HomeSection, Menu, PostDetail, PostSummary } from '../types';

export const NewsService = {
  getHomeData: async () => {
    const response = await api.get<HomeSection[]>('/home/');
    return response.data;
  },

  getMenus: async () => {
    const response = await api.get<Menu[]>('/menus/');
    return response.data;
  },

  getPostBySlug: async (slug: string) => {
    const response = await api.get<PostDetail>(`/posts/${slug}/`);
    return response.data;
  },

  getPosts: async (params?: { category?: string; search?: string; tag?: string }) => {
    const response = await api.get<PostSummary[]>('/posts/', { params });
    return response.data;
  }
};