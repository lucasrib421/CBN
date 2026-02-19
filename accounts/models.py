import uuid

from django.contrib.auth.models import User
from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'role'
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'

    def __str__(self):
        return self.name


class Author(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='author_profile',
        null=True,
        blank=True,
    )
    keycloak_id = models.UUIDField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=150, null=False, blank=False, db_index=True)
    bio = models.TextField(null=True, blank=True)
    avatar = models.ForeignKey(
        'media_app.Media',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='author_avatars',
    )
    role = models.ForeignKey('accounts.Role', on_delete=models.PROTECT, null=True, blank=True)
    managed_categories = models.ManyToManyField('content.Category', blank=True)

    class Meta:
        ordering = ['name']
        db_table = 'author'
        verbose_name_plural = 'Autores'

    def __str__(self):
        return self.name
