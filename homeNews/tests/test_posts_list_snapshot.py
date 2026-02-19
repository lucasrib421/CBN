import pytest

from homeNews.tests.helpers import assert_keys


pytestmark = pytest.mark.django_db


def test_posts_list_snapshot_shape(api_client, public_post):
    response = api_client.get('/api/v1/posts/')

    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {'count', 'next', 'previous', 'results'}
    assert isinstance(data['results'], list)
    assert len(data['results']) >= 1
    assert_keys(
        data['results'][0],
        {
            'id',
            'title',
            'subtitle',
            'slug',
            'cover_image',
            'author',
            'categories',
            'published_at',
            'reading_time',
            'created_at',
        },
    )
    assert data['results'][0]['slug'] == public_post.slug
