from django.db import models


class PostStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Rascunho'
    PUBLISHED = 'PUBLISHED', 'Publicado'
    ARCHIVED = 'ARCHIVED', 'Arquivado'

class Category(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(max_length=100, unique=True, null=False, blank=False)
    color = models.CharField(max_length=7, null=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        db_table = 'category'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(max_length=100, unique=True, null=False, blank=False)

    class Meta:
        ordering = ['name']
        db_table = 'tag'

    def __str__(self):
        return self.name


class Post(models.Model):
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
    author = models.ForeignKey('accounts.Author', on_delete=models.CASCADE, null=False, blank=False)
    categories = models.ManyToManyField('content.Category', blank=False)
    tags = models.ManyToManyField('content.Tag', blank=True)
    status = models.CharField(
        max_length=20,
        choices=PostStatus.choices,
        default=PostStatus.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']
        db_table = 'post'

    def __str__(self):
        return self.title
