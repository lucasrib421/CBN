from dataclasses import dataclass

from django.db import transaction
from rest_framework import serializers

from accounts.services.editorial_roles import ResolvedEditorialRole, resolve_editorial_role
from content.models import Category, Post, Tag
from content.services.editorial_workflow import (
    EditorialPermissionDeniedError,
    InvalidEditorialTransitionError,
    get_default_editorial_workflow_service,
)
from home.models import HomeSection, HomeSectionItem
from media_app.models import Media
from navigation.models import Menu, MenuItem


@dataclass(frozen=True)
class _WorkflowTransitionContext:
    from_status: str
    to_status: str
    actor: ResolvedEditorialRole
    should_audit: bool


class PainelMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'file', 'title', 'alt_text', 'image_type', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'color', 'is_active']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id']


class PostReadSerializer(serializers.ModelSerializer):
    author_id = serializers.UUIDField(source='author.id', read_only=True)
    author_name = serializers.CharField(source='author.name', read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    cover_image = PainelMediaSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'subtitle',
            'slug',
            'content',
            'status',
            'published_at',
            'reading_time',
            'created_at',
            'updated_at',
            'author_id',
            'author_name',
            'categories',
            'tags',
            'cover_image',
        ]


class PostWriteSerializer(serializers.ModelSerializer):
    _workflow_transition_context: _WorkflowTransitionContext | None = None

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'subtitle',
            'slug',
            'content',
            'status',
            'published_at',
            'categories',
            'tags',
            'cover_image',
        ]
        read_only_fields = ['id']

    def _request_token_payload(self) -> dict | None:
        request = self.context.get('request')
        if request is None:
            return None
        token = getattr(request, 'auth', None)
        payload = getattr(token, 'payload', None)
        if isinstance(payload, dict):
            return payload
        return None

    def _resolve_actor(self) -> ResolvedEditorialRole:
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is not None and not getattr(user, 'is_authenticated', False):
            user = None
        return resolve_editorial_role(user=user, token_payload=self._request_token_payload())

    def validate(self, attrs):
        attrs = super().validate(attrs)
        actor = self._resolve_actor()
        workflow = get_default_editorial_workflow_service()

        current_status = self.instance.status if self.instance else Post.status.field.default
        target_status = attrs.get('status', current_status)

        current_published_at = self.instance.published_at if self.instance else None
        target_published_at = attrs.get('published_at', current_published_at)
        published_at_changed = current_published_at != target_published_at

        try:
            result = workflow.validate_transition(
                current_status=current_status,
                target_status=target_status,
                published_at=target_published_at,
                actor=actor,
                published_at_changed=published_at_changed,
            )
        except InvalidEditorialTransitionError as exc:
            raise serializers.ValidationError({'status': str(exc)})
        except EditorialPermissionDeniedError as exc:
            raise serializers.ValidationError({'status': str(exc)})

        attrs['published_at'] = result.normalized_published_at
        self._workflow_transition_context = _WorkflowTransitionContext(
            from_status=current_status,
            to_status=target_status,
            should_audit=result.should_audit,
            actor=actor,
        )
        return attrs

    def _record_transition_if_needed(self, post: Post) -> None:
        context = self._workflow_transition_context
        if context is None or not context.should_audit:
            return

        workflow = get_default_editorial_workflow_service()

        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is not None and not getattr(user, 'is_authenticated', False):
            user = None

        workflow.record_transition(
            post=post,
            from_status=context.from_status,
            to_status=context.to_status,
            user=user,
            actor_role=context.actor.role,
        )

    @transaction.atomic
    def create(self, validated_data):
        post = super().create(validated_data)
        self._record_transition_if_needed(post)
        return post

    @transaction.atomic
    def update(self, instance, validated_data):
        post = super().update(instance, validated_data)
        self._record_transition_if_needed(post)
        return post


class HomeSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeSection
        fields = ['id', 'title', 'section_type', 'order', 'is_active']
        read_only_fields = ['id']


class HomeSectionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeSectionItem
        fields = ['id', 'section', 'post', 'order']
        read_only_fields = ['id']


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'title', 'slug', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'menu', 'parent', 'label', 'url', 'order', 'target', 'is_active']
        read_only_fields = ['id']
