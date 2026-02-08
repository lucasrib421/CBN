import pytest

from homeNews.tests.helpers import assert_keys


pytestmark = pytest.mark.django_db


def test_categories_snapshot_shape(api_client, public_post):
    response = api_client.get('/api/categories/')

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert_keys(data[0], {'id', 'name', 'slug', 'color'})
