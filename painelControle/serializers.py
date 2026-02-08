from rest_framework import serializers
from setup.models import Media, Category, Tag, Post, HomeSection, HomeSectionItem, Menu, MenuItem

# Serializer que devem ser feitos
# Media, Category, Tag, Post, HomeSection, HomeSectionItem, Menu, MenuItem

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'file', 'alt_text', 'uploaded_at']
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

class PostSerializer(serializers.ModelSerializer):
    author_info = serializers.PrimaryKeyRelatedField(source='author', read_only=True)
    categories_info = serializers.StringRelatedField(many=True, source='categories', read_only=True)
    tags_info = serializers.StringRelatedField(many=True, source='tags', read_only=True)
    cover_image_info = MediaSerializer(source='cover_image', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'subtitle', 'slug', 'content', 'status', 'created_at', 'updated_at',
                  'author_info', 'categories_info', 'tags_info', 'cover_image_info', # Read-only fields
                  'author', 'categories', 'tags', 'cover_image' # Write-only fields
                ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'author': {'write_only': True},
            'categories': {'write_only': True},
            'tags': {'write_only': True},
            'cover_image': {'write_only': True},
        }

        def get_author_info(self, obj):
            return {'id': obj.author.id, 'name': obj.author.name}

class HomeSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeSection
        fields = ['id', 'title', 'section_type', 'order', 'is_active']
        read_only_fields = ['id']

class HomeSectionItemSerializer(serializers.ModelSerializer):
    section_info = serializers.StringRelatedField(read_only=True)
    post_info = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = HomeSectionItem 
        fields = ['id', 'order',
        'section', 'post',
        'section_info', 'post_info']
        read_only_fields = ['id']

        extra_kwargs = {
            'section': {'write_only': True},
            'post': {'write_only': True},
        }

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'title', 'slug', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class MenuItemSerializer(serializers.ModelSerializer):
    menu_info = serializers.StringRelatedField(read_only=True)
    parent_info = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'label', 'url', 'order', 'target', 'is_active',
                  'menu', 'parent',
                  'menu_info', 'parent_info']
        read_only_fields = ['id']  
        extra_kwargs = {
            'menu': {'write_only': True},
            'parent': {'write_only': True},
        }
