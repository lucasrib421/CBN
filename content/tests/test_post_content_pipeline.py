import pytest
from django.contrib.auth.models import User

from accounts.models import Author
from content.models import Post, PostStatus
from content.services.html_sanitizer import BleachHtmlSanitizer
from content.services.plain_text_extractor import HtmlPlainTextExtractor
from content.services.post_content_pipeline import PostContentPipeline
from content.services.reading_time_calculator import WordCountReadingTimeCalculator


pytestmark = pytest.mark.django_db


def test_html_sanitizer_removes_malicious_payloads():
    sanitizer = BleachHtmlSanitizer()
    raw_html = (
        '<p onclick="alert(1)">texto</p>'
        '<script>alert("xss")</script>'
        '<a href="javascript:alert(1)">link</a>'
    )

    sanitized = sanitizer.sanitize(raw_html)

    assert '<script' not in sanitized
    assert 'onclick=' not in sanitized
    assert 'javascript:' not in sanitized
    assert 'alert("xss")' not in sanitized


def test_html_sanitizer_preserves_whitelisted_tags_and_attributes():
    sanitizer = BleachHtmlSanitizer()
    raw_html = (
        '<h2>Titulo</h2>'
        '<p><strong>forte</strong> e <em>italico</em></p>'
        '<a href="https://cbn.com" target="_blank" rel="noopener">site</a>'
        '<a href="/categoria/politica">interna</a>'
        '<a href="#topo">anchor</a>'
        '<blockquote>citacao</blockquote>'
    )

    sanitized = sanitizer.sanitize(raw_html)

    assert '<h2>Titulo</h2>' in sanitized
    assert '<strong>forte</strong>' in sanitized
    assert '<em>italico</em>' in sanitized
    assert '<blockquote>citacao</blockquote>' in sanitized
    assert 'href="https://cbn.com"' in sanitized
    assert 'href="/categoria/politica"' in sanitized
    assert 'href="#topo"' in sanitized
    assert 'target="_blank"' in sanitized


def test_reading_time_calculator_returns_none_for_empty_text():
    calculator = WordCountReadingTimeCalculator(words_per_minute=200)
    assert calculator.calculate_minutes('') is None


def test_reading_time_calculator_rounds_up_words_per_minute():
    calculator = WordCountReadingTimeCalculator(words_per_minute=200)
    text = 'palavra ' * 201

    assert calculator.calculate_minutes(text) == 2


def test_pipeline_sanitizes_html_and_calculates_reading_time():
    pipeline = PostContentPipeline(
        sanitizer=BleachHtmlSanitizer(),
        plain_text_extractor=HtmlPlainTextExtractor(),
        reading_time_calculator=WordCountReadingTimeCalculator(words_per_minute=100),
    )

    processed = pipeline.process('<h2>Titulo</h2><p>um dois tres quatro</p><script>x</script>')

    assert '<script' not in processed.sanitized_html
    assert processed.plain_text == 'Titulo um dois tres quatro'
    assert processed.reading_time == 1


def test_post_save_applies_content_pipeline_automatically():
    user = User.objects.create_user(username='post-content-pipeline', password='secret')
    author = Author.objects.create(user=user, name='Autor Pipeline')
    post = Post.objects.create(
        title='Post seguro',
        subtitle='Sub',
        slug='post-seguro',
        content='<p>texto inicial</p><script>alert(1)</script>',
        author=author,
        status=PostStatus.DRAFT,
    )

    post.refresh_from_db()

    assert '<script' not in post.content
    assert post.content == '<p>texto inicial</p>'
    assert post.reading_time == 1


def test_post_partial_save_without_content_does_not_run_pipeline(monkeypatch: pytest.MonkeyPatch):
    user = User.objects.create_user(username='post-no-content-update', password='secret')
    author = Author.objects.create(user=user, name='Autor Sem Conteudo')
    post = Post.objects.create(
        title='Post base',
        subtitle='Sub',
        slug='post-base',
        content='<p>texto inicial</p>',
        author=author,
        status=PostStatus.DRAFT,
    )

    original_content = post.content
    original_reading_time = post.reading_time
    pipeline_called = False

    def _track_pipeline(_self):
        nonlocal pipeline_called
        pipeline_called = True

    monkeypatch.setattr(Post, '_process_content', _track_pipeline)

    post.status = PostStatus.PUBLISHED
    post.save(update_fields=['status'])
    post.refresh_from_db()

    assert pipeline_called is False
    assert post.content == original_content
    assert post.reading_time == original_reading_time
    assert post.status == PostStatus.PUBLISHED


def test_post_partial_save_with_content_runs_pipeline_and_persists_reading_time(
    monkeypatch: pytest.MonkeyPatch,
):
    user = User.objects.create_user(username='post-content-update', password='secret')
    author = Author.objects.create(user=user, name='Autor Com Conteudo')
    post = Post.objects.create(
        title='Post base 2',
        subtitle='Sub',
        slug='post-base-2',
        content='<p>texto inicial</p>',
        author=author,
        status=PostStatus.DRAFT,
    )

    pipeline_called = False

    def _fake_pipeline(instance: Post):
        nonlocal pipeline_called
        pipeline_called = True
        instance.content = '<p>conteudo sanitizado</p>'
        instance.reading_time = 5

    monkeypatch.setattr(Post, '_process_content', _fake_pipeline)

    post.content = '<p>conteudo novo</p><script>xss</script>'
    post.save(update_fields=['content'])
    post.refresh_from_db()

    assert pipeline_called is True
    assert post.content == '<p>conteudo sanitizado</p>'
    assert post.reading_time == 5
