import pytest

from homeNews.tests.helpers import assert_keys


pytestmark = pytest.mark.django_db


def test_posts_list_snapshot_shape(api_client, public_post):
    response = api_client.get('/api/posts/')

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert_keys(
        data[0],
        {
            'id',
            'title',
            'subtitle',
            'slug',
            'cover_image',
            'author',
            'categories',
            'created_at',
        },
    )
    assert data[0]['slug'] == public_post.slug
