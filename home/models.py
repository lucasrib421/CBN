from django.db import models


class HomeSectionType(models.TextChoices):
    CAROUSEL = 'CAROUSEL', 'Carrossel'
    HIGHLIGHTS = 'HIGHLIGHTS', 'Destaques'
    GRID = 'GRID', 'Grade'
    LIST = 'LIST', 'Lista'
    SIDEBAR = 'SIDEBAR', 'Barra lateral'


class HomeSection(models.Model):
    class HomeSectionQuerySet(models.QuerySet):
        def active(self):
            return self.filter(is_active=True)

    title = models.CharField(max_length=100, null=False, blank=False)
    section_type = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        choices=HomeSectionType.choices,
        default=HomeSectionType.HIGHLIGHTS,
    )
    order = models.IntegerField(null=False, blank=False)
    is_active = models.BooleanField(default=True)

    objects = HomeSectionQuerySet.as_manager()

    class Meta:
        ordering = ['order']
        db_table = 'home_section'
        verbose_name_plural = 'Seções da Home'

    def __str__(self):
        return self.title


class HomeSectionItem(models.Model):
    section = models.ForeignKey(
        'home.HomeSection',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='items',
    )
    post = models.ForeignKey(
        'content.Post',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='section_appearances',
    )
    order = models.IntegerField(null=False, blank=False)

    class Meta:
        ordering = ['order']
        db_table = 'home_section_item'
        constraints = [
            models.UniqueConstraint(fields=['section', 'post'], name='unique_home_section_post'),
            models.UniqueConstraint(fields=['section', 'order'], name='unique_home_section_order'),
        ]
        verbose_name_plural = 'Itens da Home'

    def __str__(self):
        return f'{self.section.title} - {self.post.title}'
