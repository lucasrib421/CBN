from rest_framework import serializers

from content.models import Category, Post, Tag
from home.models import HomeSection, HomeSectionItem
from media_app.models import Media
from navigation.models import Menu, MenuItem


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
            'categories',
            'tags',
            'cover_image',
        ]
        read_only_fields = ['id']


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
