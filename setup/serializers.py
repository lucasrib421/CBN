from rest_framework import serializers
from .models import HomeConfig, Post, Category, Media

# --- SERIALIZERS AUXILIARES (Para exibir cards na home) ---

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'file', 'alt_text']

class CategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class PostCardSerializer(serializers.ModelSerializer):
    """
    Versão leve do Post apenas para cards (sem o conteúdo do texto).
    """
    author_name = serializers.CharField(source='author.name', read_only=True)
    category = CategorySimpleSerializer(read_only=True)
    cover = MediaSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'sub_title', 'slug', 'author_name', 'category', 'cover', 'published_at']