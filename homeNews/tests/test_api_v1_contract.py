import pytest


pytestmark = pytest.mark.django_db


def test_v1_posts_is_paginated(api_client, public_post):
    response = api_client.get('/api/v1/posts/')

    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {'count', 'next', 'previous', 'results'}
    assert isinstance(data['results'], list)
    assert data['results'][0]['slug'] == public_post.slug


def test_v1_redirects_endpoint_available(api_client):
    response = api_client.get('/api/v1/redirects/')

    assert response.status_code == 200
