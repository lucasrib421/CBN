from datetime import timedelta

import pytest
from django.utils import timezone

from content.models import PostStatus
from setup.tests.factories import PostFactory


pytestmark = pytest.mark.django_db


def test_public_endpoint_hides_future_published_posts(api_client):
    past_post = PostFactory(
        status=PostStatus.PUBLISHED,
        published_at=timezone.now() - timedelta(minutes=5),
    )
    PostFactory(
        status=PostStatus.PUBLISHED,
        published_at=timezone.now() + timedelta(hours=6),
    )

    response = api_client.get('/api/v1/posts/')

    assert response.status_code == 200
    slugs = {result['slug'] for result in response.json()['results']}
    assert past_post.slug in slugs
    assert len(slugs) == 1
