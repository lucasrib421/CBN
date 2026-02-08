import pytest
from django.contrib.auth.models import User

from accounts.models import Author
from content.models import Post, PostStatus


pytestmark = pytest.mark.django_db


def test_post_status_filter_supports_textchoices():
    user = User.objects.create_user(username='autor-status', password='secret')
    author = Author.objects.create(user=user, name='Autor')
    draft = Post.objects.create(
        title='Rascunho',
        subtitle='Sub',
        slug='rascunho',
        content='Conteudo',
        author=author,
        status=PostStatus.DRAFT,
    )
    published = Post.objects.create(
        title='Publicado',
        subtitle='Sub',
        slug='publicado',
        content='Conteudo',
        author=author,
        status=PostStatus.PUBLISHED,
    )

    published_ids = set(Post.objects.filter(status=PostStatus.PUBLISHED).values_list('id', flat=True))

    assert published.id in published_ids
    assert draft.id not in published_ids


def test_post_default_status_is_draft():
    user = User.objects.create_user(username='autor-default', password='secret')
    author = Author.objects.create(user=user, name='Autor 2')
    post = Post.objects.create(
        title='Sem status explicito',
        subtitle='Sub',
        slug='sem-status-explicito',
        content='Conteudo',
        author=author,
    )

    assert post.status == PostStatus.DRAFT
