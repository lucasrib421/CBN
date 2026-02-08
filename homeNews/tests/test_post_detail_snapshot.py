import pytest

from homeNews.tests.helpers import assert_keys


pytestmark = pytest.mark.django_db


def test_posts_detail_snapshot_shape(api_client, public_post):
    response = api_client.get(f'/api/posts/{public_post.slug}/')

    assert response.status_code == 200
    data = response.json()
    assert_keys(
        data,
        {
            'id',
            'title',
            'subtitle',
            'slug',
            'content',
            'cover_image',
            'author',
            'categories',
            'tags',
            'published_at',
            'reading_time',
            'created_at',
            'updated_at',
        },
    )
