import pytest
from django.contrib.auth.models import User
from django.core.cache import cache

from accounts.models import Author
from content.models import Category, Post, PostStatus
from homeNews.cache_utils import build_cache_key


pytestmark = pytest.mark.django_db


def _build_post(slug: str) -> Post:
    user = User.objects.create_user(username=f'user-{slug}', password='secret')
    author = Author.objects.create(user=user, name=f'Author {slug}')
    category = Category.objects.create(
        name=f'Category {slug}', slug=f'cat-{slug}', color='#123456', is_active=True
    )
    post = Post.objects.create(
        title=f'Post {slug}',
        subtitle='Sub',
        slug=slug,
        content='Conteudo',
        author=author,
        status=PostStatus.PUBLISHED,
    )
    post.categories.add(category)
    return post


def test_posts_list_cache_key_is_written(api_client):
    cache.clear()
    post = _build_post('cache-list')

    response = api_client.get('/api/v1/posts/')

    assert response.status_code == 200
    key = build_cache_key('posts-list', '/api/v1/posts/')
    cached = cache.get(key)
    assert cached is not None
    assert cached['results'][0]['slug'] == post.slug


def test_post_save_invalidates_posts_cache(api_client):
    cache.clear()
    _build_post('cache-invalidate-a')

    first_response = api_client.get('/api/v1/posts/')
    assert first_response.status_code == 200
    key = build_cache_key('posts-list', '/api/v1/posts/')
    assert cache.get(key) is not None

    _build_post('cache-invalidate-b')

    assert cache.get(key) is None
