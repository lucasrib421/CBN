from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.response import Response

from content.models import Category, Post, Tag
from home.models import HomeSection
from homeNews.cache_utils import CACHE_TTLS, build_cache_key, set_cache_headers
from homeNews.filters import PostFilter
from homeNews.serializers import (
    CategorySerializer,
    HomeSectionSerializer,
    MenuSerializer,
    PostDetailSerializer,
    PostListSerializer,
    RedirectSerializer,
    TagSerializer,
)
from navigation.models import Menu, Redirect


class CachedReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    cache_prefix = ''
    cache_ttl = 60

    def _cache_key(self) -> str:
        return build_cache_key(self.cache_prefix, self.request.get_full_path())

    def list(self, request, *args, **kwargs):
        key = self._cache_key()
        cached = cache.get(key)
        if cached is not None:
            response = Response(cached)
            set_cache_headers(response, self.cache_ttl)
            return response

        response = super().list(request, *args, **kwargs)
        cache.set(key, response.data, timeout=self.cache_ttl)
        set_cache_headers(response, self.cache_ttl)
        return response

    def retrieve(self, request, *args, **kwargs):
        key = self._cache_key()
        cached = cache.get(key)
        if cached is not None:
            response = Response(cached)
            set_cache_headers(response, self.cache_ttl)
            return response

        response = super().retrieve(request, *args, **kwargs)
        cache.set(key, response.data, timeout=self.cache_ttl)
        set_cache_headers(response, self.cache_ttl)
        return response


class PostViewSet(CachedReadOnlyViewSet):
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['title', 'subtitle', 'content']
    ordering_fields = ['published_at', 'created_at', 'title']
    ordering = ['-published_at', '-created_at']
    cache_prefix = 'posts-list'
    cache_ttl = CACHE_TTLS['posts_list']

    def get_queryset(self):
        return (
            Post.objects.published()
            .select_related('author', 'author__avatar', 'cover_image')
            .prefetch_related('categories', 'tags')
            .order_by('-published_at', '-created_at')
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return PostDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        self.cache_prefix = 'post-detail'
        self.cache_ttl = CACHE_TTLS['post_detail']
        return super().retrieve(request, *args, **kwargs)


class CategoryViewSet(CachedReadOnlyViewSet):
    queryset = Category.objects.active()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    pagination_class = None
    cache_prefix = 'categories'
    cache_ttl = CACHE_TTLS['categories']


class TagViewSet(CachedReadOnlyViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    pagination_class = None
    cache_prefix = 'tags'
    cache_ttl = CACHE_TTLS['tags']


class HomeViewSet(CachedReadOnlyViewSet):
    serializer_class = HomeSectionSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    cache_prefix = 'home'
    cache_ttl = CACHE_TTLS['home']

    def get_queryset(self):
        return (
            HomeSection.objects.active()
            .prefetch_related(
                'items',
                'items__post',
                'items__post__author',
                'items__post__cover_image',
                'items__post__categories',
            )
            .order_by('order')
        )


class MenuViewSet(CachedReadOnlyViewSet):
    serializer_class = MenuSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    pagination_class = None
    cache_prefix = 'menus'
    cache_ttl = CACHE_TTLS['menus']

    def get_queryset(self):
        return Menu.objects.active().prefetch_related(
            'menuitem_set',
            'menuitem_set__children',
            'menuitem_set__children__children',
        )


class RedirectViewSet(CachedReadOnlyViewSet):
    queryset = Redirect.objects.filter(is_active=True)
    serializer_class = RedirectSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    cache_prefix = 'redirects'
    cache_ttl = CACHE_TTLS['redirects']
