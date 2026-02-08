from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from setup.models import Post, Category, HomeSection, Menu, Tag
from .serializers import (
    PostListSerializer, 
    PostDetailSerializer, 
    CategorySerializer, 
    HomeSectionSerializer, 
    MenuSerializer,
    TagSerializer
)
from setup.serializers import (
    MediaSerializer,
    CategorySimpleSerializer,
    PostCardSerializer
)
from .filters import PostFilter

#Criar ViewSet para Author futuramente, porém mapear apenas os campos de nome, bio e avatar.

class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API pública de Notícias.
    Lista: Retorna cards leves.
    Detalhe: Retorna a notícia completa.
    """
    lookup_field = 'slug' # Vamos buscar por /api/posts/minha-noticia-legal/
    permission_classes = [permissions.AllowAny] # Aberto ao público
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PostFilter
    search_fields = ['title', 'subtitle', 'content'] # Busca textual

    def get_queryset(self):
        # Otimização CRÍTICA:
        # select_related: Busca FKs na mesma query (Autor, Categoria, Imagem)
        # prefetch_related: Busca M2M em query separada mas otimizada (Tags)
        queryset = Post.objects.filter(status__name='PUBLISHED').select_related(
            'author', 'author__avatar', 'cover_image'
        ).prefetch_related(
            'categories', 'tags'
        ).order_by('-created_at')
        
        return queryset

    def get_serializer_class(self):
        # Se for listagem (cards), usa o leve. Se for detalhe, usa o completo.
        if self.action == 'list':
            return PostListSerializer
        return PostDetailSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    pagination_class = None # Categorias geralmente não precisam de paginação

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    pagination_class = None

class HomeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retorna a estrutura da Home Page inteira.
    Geralmente o front chama apenas /api/home/ (list)
    """
    serializer_class = HomeSectionSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None # A home é uma página única, sem paginação

    def get_queryset(self):
        return HomeSection.objects.filter(is_active=True).prefetch_related(
            'homesectionitem_set', # Pega os itens da seção
            'homesectionitem_set__post', # Pega o post de cada item
            'homesectionitem_set__post__author', # Pega o autor do post
            'homesectionitem_set__post__cover_image', # Pega a imagem
            'homesectionitem_set__post__categories' # Pega as categorias
        ).order_by('order')

class MenuViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Menus do site (Header, Footer, etc).
    """
    serializer_class = MenuSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    pagination_class = None

    def get_queryset(self):
        # Aqui resolvemos o problema N+1 do Menu
        return Menu.objects.filter(is_active=True).prefetch_related(
            'menuitem_set', # Pega os itens raiz
            'menuitem_set__children', # Pega os filhos (nível 1)
            'menuitem_set__children__children' # Pega os netos (nível 2 - se houver)
        )