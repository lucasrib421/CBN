import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError

from accounts.models import Author
from content.models import Category, Post, PostStatus
from home.models import HomeSection, HomeSectionItem


pytestmark = pytest.mark.django_db


def _post(slug: str, title: str, username: str) -> Post:
    user = User.objects.create_user(username=username, password='secret')
    author = Author.objects.create(user=user, name=username)
    post = Post.objects.create(
        title=title,
        subtitle='Sub',
        slug=slug,
        content='Conteudo',
        author=author,
        status=PostStatus.PUBLISHED,
    )
    category = Category.objects.create(
        name=f'Categoria-{slug}', slug=f'categoria-{slug}', color='#123456', is_active=True
    )
    post.categories.add(category)
    return post


def test_unique_home_section_post_constraint():
    section = HomeSection.objects.create(
        title='Destaques', section_type='HIGHLIGHTS', order=1, is_active=True
    )
    post = _post('post-constraint-1', 'Post 1', 'constraint-user-1')

    HomeSectionItem.objects.create(section=section, post=post, order=1)

    with pytest.raises(IntegrityError):
        HomeSectionItem.objects.create(section=section, post=post, order=2)


def test_unique_home_section_order_constraint():
    section = HomeSection.objects.create(
        title='Top', section_type='HIGHLIGHTS', order=2, is_active=True
    )
    post_a = _post('post-constraint-2a', 'Post 2A', 'constraint-user-2a')
    post_b = _post('post-constraint-2b', 'Post 2B', 'constraint-user-2b')

    HomeSectionItem.objects.create(section=section, post=post_a, order=1)

    with pytest.raises(IntegrityError):
        HomeSectionItem.objects.create(section=section, post=post_b, order=1)
