from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from accounts.services.editorial_roles import resolve_editorial_role
from content.models import Category, Post, PostStatus, Tag
from content.services.editorial_workflow import get_default_editorial_workflow_service
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
    queryset = Post.objects.select_related('author', 'cover_image').prefetch_related(
        'categories', 'tags'
    )
    search_fields = ['title', 'subtitle', 'content', 'slug']
    ordering_fields = ['published_at', 'created_at', 'title']
    ordering = ['-published_at', '-created_at']
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrAdmin]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PostReadSerializer
        return PostWriteSerializer

    def perform_create(self, serializer):
        author = getattr(self.request.user, 'author_profile', None)
        if author is None:
            raise ValidationError({'author': 'Usuário não possui perfil de autor vinculado.'})
        serializer.save(author=author)

    def perform_update(self, serializer):
        serializer.save(author=serializer.instance.author)

    @action(detail=False, methods=['get'], url_path='available-transitions')
    def available_transitions(self, request):
        current_status = request.query_params.get('status', PostStatus.DRAFT)
        if current_status not in PostStatus.values:
            return Response(
                {'detail': f'Status inválido: {current_status}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = getattr(request, 'auth', None)
        token_payload = getattr(token, 'payload', None)
        if not isinstance(token_payload, dict):
            token_payload = None

        actor = resolve_editorial_role(
            user=request.user,
            token_payload=token_payload,
        )
        workflow = get_default_editorial_workflow_service()
        allowed = workflow.allowed_transitions(
            current_status=current_status,
            actor=actor,
        )

        return Response(
            {
                'current_status': current_status,
                'allowed_transitions': list(allowed),
                'labels': workflow.as_label_map(),
                'effective_role': actor.role.slug if actor.role else None,
                'role_source': actor.source,
                'can_publish_directly': actor.can_publish_directly,
            }
        )


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
