from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, DjangoModelPermissions
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from datetime import timedelta

from setup.models import Media, Category, Tag, Post, HomeSection, HomeSectionItem, Menu, MenuItem
from homeNews.serializers import (
    MediaSerializer, CategorySerializer, TagSerializer, PostSerializer, 
    HomeSectionSerializer, HomeSectionItemSerializer, MenuSerializer, MenuItemSerializer
)

#from .filters import PostFilter, CategoryFilter
#from .pagination import StandardResultsSetPagination, LargeResultsSetPagination
#from .throttling import PostCreateRateThrottle, PostUpdateRateThrottle

# Create your views here.
class BaseViewSet(viewsets.ModelViewSet):
    """
    A base viewset that provides default `list()`, `create()`, `retrieve()`,
    `update()`, and `destroy()` actions.
    """
    permission_classes = [IsAuthenticated]  # Define your permission classes here
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        """
        Sobrescreva este método em ViewSets filhos para filtros personalizados
        """
        return super().get_queryset()
    
    def get_permissions(self):
        """
        Permissões dinâmicas baseadas na ação
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthorOrReadOnly()]
        elif self.action in ['destroy']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """
        Hook para ações durante a criação
        """
        # Exemplo: Adiciona o usuário atual como autor
        if hasattr(self.request.user, 'author_profile'):
            serializer.save(author=self.request.user.author_profile)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        """
        Hook para ações durante a atualização
        """
        # Exemplo: Registra quem modificou
        serializer.save(updated_by=self.request.user)



# Media, Category, Tag, Post, HomeSection, HomeSectionItem, Menu, MenuItem

class MediaViewSet(BaseViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    search_fields = ['alt_text']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

