import django_filters
from content.models import Post


class PostFilter(django_filters.FilterSet):
    # Permite buscar parte do título (ex: ?title=eleicoes)
    # lookup_expr='icontains' significa: ignorar maiúsculas/minúsculas e buscar trechos
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')

    # Permite filtrar pelo slug da categoria (ex: ?category=esportes)
    # O __slug diz ao Django para olhar o campo 'slug' dentro da tabela relacionada
    category = django_filters.CharFilter(field_name='categories__slug')

    # Permite filtrar pelo slug da tag (ex: ?tag=plantao)
    tag = django_filters.CharFilter(field_name='tags__slug')

    # Permite filtrar pelo nome do autor (ex: ?author=lucas)
    author = django_filters.CharFilter(field_name='author__name', lookup_expr='icontains')

    class Meta:
        model = Post
        fields = ['status', 'slug']
