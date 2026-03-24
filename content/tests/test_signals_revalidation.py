import pytest
from unittest.mock import patch
from django.contrib.auth.models import User

from accounts.models import Author
from content.models import Post, PostStatus

# Avisa ao pytest que esses testes precisam acessar o banco de dados
pytestmark = pytest.mark.django_db


# O @patch continua aqui, interceptando a nossa Sessão HTTP com Retry antes dela ir pra internet
@patch('requests.Session.post')
def test_revalidation_called_on_published_post(mock_post):
    """Garante que salvar um post PUBLICADO dispara o webhook com a tag correta"""
    
    # 1. Configuração (Setup)
    user = User.objects.create_user(username='autor-webhook', password='secret')
    author = Author.objects.create(user=user, name='Autor Webhook')

    # 2. Ação
    Post.objects.create(
        title='Notícia Urgente',
        subtitle='Sub',
        slug='noticia-urgente',
        content='Conteudo',
        author=author,
        status=PostStatus.PUBLISHED,
    )

    # 3. Verificações (Asserts)
    # Garante que o método post() foi chamado
    assert mock_post.called is True, "O webhook deveria ter sido chamado ao publicar um post."
    
    # Captura os argumentos que foram passados para o mock
    args, kwargs = mock_post.call_args
    
    # Garante que o JSON enviado tem a tag correta
    assert kwargs['json']['tags'] == ['post-noticia-urgente']


@patch('requests.Session.post')
def test_revalidation_not_called_on_new_draft(mock_post):
    """Garante que criar um RASCUNHO novo não dispara o webhook"""
    
    # 1. Configuração (Setup)
    user = User.objects.create_user(username='autor-rascunho', password='secret')
    author = Author.objects.create(user=user, name='Autor Rascunho')

    # 2. Ação
    Post.objects.create(
        title='Rascunho Incompleto',
        subtitle='Sub',
        slug='rascunho-incompleto',
        content='Ainda escrevendo...',
        author=author,
        status=PostStatus.DRAFT,
    )

    # 3. Verificação (Assert)
    # Garante que o método post() NÃO foi chamado
    assert mock_post.called is False, "O webhook NÃO deveria ser chamado ao criar rascunhos."