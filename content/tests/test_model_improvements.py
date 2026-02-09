import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.models import Author
from content.models import Category, Post, PostStatus


pytestmark = pytest.mark.django_db


def _author(name: str, username: str) -> Author:
    user = User.objects.create_user(username=username, password='secret')
    return Author.objects.create(user=user, name=name)


def test_post_queryset_published_and_recent():
    author = _author('Autor', 'autor-managers')
    category = Category.objects.create(
        name='Categoria', slug='categoria', color='#112233', is_active=True
    )

    first = Post.objects.create(
        title='Primeiro',
        subtitle='Sub',
        slug='primeiro',
        content='Conteudo',
        author=author,
        status=PostStatus.DRAFT,
        published_at=timezone.now(),
    )
    second = Post.objects.create(
        title='Segundo',
        subtitle='Sub',
        slug='segundo',
        content='Conteudo',
        author=author,
        status=PostStatus.PUBLISHED,
        published_at=timezone.now(),
    )
    second.categories.add(category)
    first.categories.add(category)

    published_ids = set(Post.objects.published().values_list('id', flat=True))
    recent_ids = list(Post.objects.recent(1).values_list('id', flat=True))

    assert second.id in published_ids
    assert first.id not in published_ids
    assert len(recent_ids) == 1


def test_category_color_validator_rejects_invalid_hex():
    category = Category(
        name='Categoria Invalida', slug='categoria-invalida', color='invalid', is_active=True
    )

    with pytest.raises(ValidationError):
        category.full_clean()


def test_category_queryset_active():
    Category.objects.create(name='Ativa', slug='ativa', color='#000000', is_active=True)
    Category.objects.create(name='Inativa', slug='inativa', color='#000000', is_active=False)

    slugs = set(Category.objects.active().values_list('slug', flat=True))

    assert slugs == {'ativa'}
