from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from content.services.post_content_pipeline import get_default_post_content_pipeline


class PostStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Rascunho'
    REVIEW = 'REVIEW', 'Em revisão'
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
            now = timezone.now()
            return self.filter(status=PostStatus.PUBLISHED).filter(
                models.Q(published_at__isnull=True) | models.Q(published_at__lte=now)
            )

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

    def _process_content(self) -> None:
        processed = get_default_post_content_pipeline().process(self.content)
        self.content = processed.sanitized_html
        self.reading_time = processed.reading_time

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        is_new = self.pk is None
        should_process_content = is_new or update_fields is None or 'content' in update_fields

        if should_process_content:
            self._process_content()

            if update_fields is not None:
                fields = set(update_fields)
                fields.update({'content', 'reading_time'})
                kwargs['update_fields'] = tuple(sorted(fields))

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PostStatusTransition(models.Model):
    post = models.ForeignKey(
        'content.Post',
        on_delete=models.CASCADE,
        related_name='status_transitions',
    )
    from_status = models.CharField(max_length=20, choices=PostStatus.choices)
    to_status = models.CharField(max_length=20, choices=PostStatus.choices)
    changed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='post_status_transitions',
    )
    actor_role = models.ForeignKey(
        'accounts.Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='post_status_transitions',
    )
    changed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    published_at_snapshot = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'post_status_transition'
        ordering = ['-changed_at']
        verbose_name = 'Transição de status do post'
        verbose_name_plural = 'Transições de status dos posts'

    def __str__(self) -> str:
        return f'{self.post_id}: {self.from_status} -> {self.to_status}'
