import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from accounts.models import Author, Role
from content.models import Category, Post, PostStatus, PostStatusTransition


pytestmark = pytest.mark.django_db


def _client_with_role(*, username: str, role_slug: str, role_name: str) -> APIClient:
    role, _ = Role.objects.get_or_create(slug=role_slug, defaults={'name': role_name})
    user = User.objects.create_user(username=username, password='secret')
    Author.objects.create(user=user, name=f'Autor {username}', role=role)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _base_payload(*, slug: str, status: str) -> dict:
    category = Category.objects.create(name=f'Categoria {slug}', slug=f'cat-{slug}', is_active=True)
    return {
        'title': f'Post {slug}',
        'subtitle': 'Sub',
        'slug': slug,
        'content': '<p>Conteúdo editorial consistente para validação.</p>',
        'status': status,
        'categories': [category.id],
        'tags': [],
        'cover_image': None,
        'published_at': None,
    }


def test_available_transitions_respect_editorial_role():
    editor_client = _client_with_role(
        username='editor-workflow',
        role_slug='editor-chefe',
        role_name='Editor Chefe',
    )
    reporter_client = _client_with_role(
        username='reporter-workflow',
        role_slug='reporter',
        role_name='Repórter',
    )

    editor_response = editor_client.get('/api/v1/painel/posts/available-transitions/?status=DRAFT')
    reporter_response = reporter_client.get(
        '/api/v1/painel/posts/available-transitions/?status=DRAFT'
    )

    assert editor_response.status_code == 200
    assert reporter_response.status_code == 200
    assert PostStatus.PUBLISHED in editor_response.json()['allowed_transitions']
    assert PostStatus.PUBLISHED not in reporter_response.json()['allowed_transitions']


def test_reporter_cannot_publish_directly():
    reporter_client = _client_with_role(
        username='reporter-publish',
        role_slug='reporter',
        role_name='Repórter',
    )
    payload = _base_payload(slug='reporter-direct', status=PostStatus.PUBLISHED)

    response = reporter_client.post('/api/v1/painel/posts/', payload, format='json')

    assert response.status_code == 400
    assert 'status' in response.json()


def test_editorial_flow_persists_audit_history_for_publish_and_unpublish():
    editor_client = _client_with_role(
        username='editor-publish',
        role_slug='editor-chefe',
        role_name='Editor Chefe',
    )
    payload = _base_payload(slug='workflow-audit', status=PostStatus.REVIEW)

    create_response = editor_client.post('/api/v1/painel/posts/', payload, format='json')
    assert create_response.status_code == 201

    post_id = create_response.json()['id']
    post = Post.objects.get(id=post_id)
    assert post.status == PostStatus.REVIEW

    publish_payload = {
        **payload,
        'title': 'Post workflow publicado',
        'status': PostStatus.PUBLISHED,
    }
    publish_response = editor_client.put(
        f'/api/v1/painel/posts/{post_id}/',
        publish_payload,
        format='json',
    )
    assert publish_response.status_code == 200

    unpublish_payload = {
        **publish_payload,
        'title': 'Post workflow despublicado',
        'status': PostStatus.DRAFT,
    }
    unpublish_response = editor_client.put(
        f'/api/v1/painel/posts/{post_id}/',
        unpublish_payload,
        format='json',
    )
    assert unpublish_response.status_code == 200

    post.refresh_from_db()
    assert post.status == PostStatus.DRAFT
    assert post.published_at is None

    transitions = list(
        PostStatusTransition.objects.filter(post=post).values_list('from_status', 'to_status')
    )
    assert (PostStatus.DRAFT, PostStatus.REVIEW) in transitions
    assert (PostStatus.REVIEW, PostStatus.PUBLISHED) in transitions
    assert (PostStatus.PUBLISHED, PostStatus.DRAFT) in transitions
