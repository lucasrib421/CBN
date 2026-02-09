from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


class PostStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Rascunho'
    PUBLISHED = 'PUBLISHED', 'Publicado'
    ARCHIVED = 'ARCHIVED', 'Arquivado'


class Category(models.Model):
    class CategoryQuerySet(models.QuerySet):
        def active(self):
            return self.filter(is_active=True)

    color_validator = RegexValidator(
        regex=r'^#[0-9A-Fa-f]{6}$',
        message='A cor deve estar no formato hexadecimal #RRGGBB.',
    )

    name = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(max_length=100, unique=True, null=False, blank=False)
    color = models.CharField(max_length=7, null=True, validators=[color_validator])
    is_active = models.BooleanField(default=False)

    all_objects = models.Manager()
    objects = CategoryQuerySet.as_manager()

    class Meta:
        ordering = ['name']
        db_table = 'category'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(max_length=100, unique=True, null=False, blank=False)

    class Meta:
        ordering = ['name']
        db_table = 'tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Post(models.Model):
    class PostQuerySet(models.QuerySet):
        def published(self):
            return self.filter(status=PostStatus.PUBLISHED)

        def by_category(self, slug):
            return self.filter(categories__slug=slug)

        def by_tag(self, slug):
            return self.filter(tags__slug=slug)

        def by_author(self, name):
            return self.filter(author__name__icontains=name)

        def recent(self, amount):
            return self.order_by('-published_at', '-created_at')[:amount]

    title = models.CharField(max_length=200, null=False, blank=False)
    subtitle = models.CharField(max_length=300, null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True, null=False, blank=False)
    content = models.TextField(null=False, blank=False)
    cover_image = models.ForeignKey(
        'media_app.Media',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts_using_image',
    )
    author = models.ForeignKey('accounts.Author', on_delete=models.PROTECT, null=False, blank=False)
    categories = models.ManyToManyField('content.Category', blank=False)
    tags = models.ManyToManyField('content.Tag', blank=True)
    status = models.CharField(
        max_length=20,
        choices=PostStatus.choices,
        default=PostStatus.DRAFT,
    )
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    reading_time = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ['-published_at', '-created_at']
        db_table = 'post'
        indexes = [
            models.Index(fields=['status', 'published_at'], name='post_status_published_idx'),
        ]
        verbose_name_plural = 'Posts'

    def clean(self):
        if self.pk and not self.categories.exists():
            raise ValidationError({'categories': 'Post precisa ter pelo menos uma categoria.'})

    def __str__(self):
        return self.title
