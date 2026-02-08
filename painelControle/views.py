from rest_framework import filters, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from content.models import Category, Post, Tag
from home.models import HomeSection, HomeSectionItem
from media_app.models import Media
from navigation.models import Menu, MenuItem
from painelControle.serializers import (
    CategorySerializer,
    HomeSectionItemSerializer,
    HomeSectionSerializer,
    MenuItemSerializer,
    MenuSerializer,
    PainelMediaSerializer,
    PostReadSerializer,
    PostWriteSerializer,
    TagSerializer,
)


class IsAuthorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        author = getattr(obj, 'author', None)
        return bool(author and author.user_id == request.user.id)


class BaseAuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]


class MediaViewSet(BaseAuthenticatedViewSet):
    queryset = Media.objects.all()
    serializer_class = PainelMediaSerializer
    search_fields = ['title', 'alt_text']
    ordering_fields = ['uploaded_at']
    ordering = ['-uploaded_at']


class CategoryViewSet(BaseAuthenticatedViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ['name', 'slug']
    ordering_fields = ['name']
    ordering = ['name']


class TagViewSet(BaseAuthenticatedViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    search_fields = ['name', 'slug']
    ordering_fields = ['name']
    ordering = ['name']


class PostViewSet(BaseAuthenticatedViewSet):
    queryset = Post.objects.select_related('author', 'cover_image').prefetch_related('categories', 'tags')
    search_fields = ['title', 'subtitle', 'content', 'slug']
    ordering_fields = ['published_at', 'created_at', 'title']
    ordering = ['-published_at', '-created_at']
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrAdmin]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PostReadSerializer
        return PostWriteSerializer


class HomeSectionViewSet(BaseAuthenticatedViewSet):
    queryset = HomeSection.objects.all()
    serializer_class = HomeSectionSerializer
    search_fields = ['title', 'section_type']
    ordering_fields = ['order', 'title']
    ordering = ['order']


class HomeSectionItemViewSet(BaseAuthenticatedViewSet):
    queryset = HomeSectionItem.objects.select_related('section', 'post')
    serializer_class = HomeSectionItemSerializer
    ordering_fields = ['order']
    ordering = ['order']


class MenuViewSet(BaseAuthenticatedViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    search_fields = ['title', 'slug']
    ordering_fields = ['title', 'created_at']
    ordering = ['title']


class MenuItemViewSet(BaseAuthenticatedViewSet):
    queryset = MenuItem.objects.select_related('menu', 'parent')
    serializer_class = MenuItemSerializer
    search_fields = ['label', 'url']
    ordering_fields = ['order', 'label']
    ordering = ['order']
