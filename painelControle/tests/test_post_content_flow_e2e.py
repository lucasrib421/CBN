import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from accounts.models import Author, Role
from content.models import Category, Post, PostStatus, Tag


pytestmark = pytest.mark.django_db


def _authenticated_client() -> tuple[APIClient, User, Author]:
    user = User.objects.create_user(username='editor-e2e', password='secret')
    role, _ = Role.objects.get_or_create(
        slug='editor-chefe',
        defaults={'name': 'Editor Chefe'},
    )
    author = Author.objects.create(user=user, name='Editor E2E', role=role)
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user, author


def _build_base_data() -> tuple[Category, Tag]:
    category = Category.objects.create(
        name='Politica',
        slug='politica',
        color='#123456',
        is_active=True,
    )
    tag = Tag.objects.create(name='Urgente', slug='urgente')
    return category, tag


def test_post_create_and_update_flow_sanitizes_html_and_sets_reading_time():
    client, _, _ = _authenticated_client()
    category, tag = _build_base_data()

    create_payload = {
        'title': 'Materia rica',
        'subtitle': 'Subtitulo',
        'slug': 'materia-rica',
        'content': (
            '<h2>Cabecalho</h2>'
            '<p>Texto seguro</p>'
            '<script>alert(1)</script>'
            '<a href="javascript:alert(1)">clique</a>'
        ),
        'status': PostStatus.DRAFT,
        'categories': [category.id],
        'tags': [tag.id],
        'cover_image': None,
        'published_at': None,
    }

    create_response = client.post('/api/v1/painel/posts/', create_payload, format='json')

    assert create_response.status_code == 201
    post_id = create_response.json()['id']
    post = Post.objects.get(id=post_id)

    assert '<script' not in post.content
    assert 'javascript:' not in post.content
    assert post.reading_time == 1

    update_payload = {
        'title': 'Materia rica atualizada',
        'subtitle': 'Subtitulo atualizado',
        'slug': 'materia-rica',
        'content': '<p>conteudo atualizado com <strong>formatacao</strong></p><img src="data:test" />',
        'status': PostStatus.PUBLISHED,
        'categories': [category.id],
        'tags': [tag.id],
        'cover_image': None,
        'published_at': None,
    }

    update_response = client.put(f'/api/v1/painel/posts/{post_id}/', update_payload, format='json')

    assert update_response.status_code == 200

    post.refresh_from_db()
    assert '<img' in post.content
    assert 'data:test' not in post.content
    assert post.status == PostStatus.PUBLISHED
    assert post.reading_time == 1

    retrieve_response = client.get(f'/api/v1/painel/posts/{post_id}/')
    assert retrieve_response.status_code == 200
    retrieve_data = retrieve_response.json()
    assert retrieve_data['content'] == post.content
    assert retrieve_data['reading_time'] == post.reading_time
