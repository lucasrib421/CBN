from rest_framework import serializers
from setup.models import Media, Category, Tag, Post, HomeSection, HomeSectionItem, Menu, MenuItem, Author

# --- Blocos Básicos ---

class MediaSerializer(serializers.ModelSerializer):
    # O DRF já converte 'file' para a URL completa automaticamente
    class Meta:
        model = Media
        fields = ['id', 'title', 'file', 'alt_text', 'image_type']

class AuthorSerializer(serializers.ModelSerializer):
    # Mostramos apenas o necessário publicamente
    avatar = MediaSerializer(read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'name', 'bio', 'avatar']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'color']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

# --- Notícias ---

class PostListSerializer(serializers.ModelSerializer):
    """
    Usado em listas e cards. NÃO traz o conteúdo (texto) para ser leve.
    """
    author = AuthorSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    cover_image = MediaSerializer(read_only=True)
    # Tags geralmente não aparecem no card da home, então removi para economizar

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'subtitle', 'slug', 
            'cover_image', 'author', 'categories', 
            'created_at'
        ]

class PostDetailSerializer(serializers.ModelSerializer):
    """
    Usado apenas quando o usuário clica na notícia. Traz TUDO.
    """
    author = AuthorSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    cover_image = MediaSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'subtitle', 'slug', 'content', 
            'cover_image', 'author', 'categories', 'tags',
            'created_at', 'updated_at'
        ]

# --- Estrutura da Home ---

class HomeSectionItemSerializer(serializers.ModelSerializer):
    # Aqui a mágica: Trazemos os dados do Post JÁ DENTRO do item
    post = PostListSerializer(read_only=True)

    class Meta:
        model = HomeSectionItem
        fields = ['id', 'order', 'post']

class HomeSectionSerializer(serializers.ModelSerializer):
    # Trazemos os itens dessa seção
    # O source='homesectionitem_set' pega o relacionamento reverso (ou related_name se tiver definido)
    items = HomeSectionItemSerializer(source='homesectionitem_set', many=True, read_only=True)

    class Meta:
        model = HomeSection
        fields = ['id', 'title', 'section_type', 'order', 'items']

# --- Menus ---

class MenuItemSerializer(serializers.ModelSerializer):
    # Campo calculado para pegar os filhos (submenus)
    children = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ['id', 'label', 'url', 'target', 'order', 'children']

    def get_children(self, obj):
        # Pega itens que têm este item como 'parent'
        children = obj.children.filter(is_active=True).order_by('order')
        return MenuItemSerializer(children, many=True).data

class MenuSerializer(serializers.ModelSerializer):
    # Pegamos apenas os itens "Raiz" (que não têm parent)
    items = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ['id', 'title', 'slug', 'items']

    def get_items(self, obj) -> list[dict[str, object]]:
        # Filtra apenas itens de primeiro nível (parent=None)
        root_items = obj.menuitem_set.filter(parent__isnull=True, is_active=True).order_by('order')
        return MenuItemSerializer(root_items, many=True).data
