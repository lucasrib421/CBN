import pytest

from homeNews.tests.helpers import assert_keys


pytestmark = pytest.mark.django_db


def test_menus_snapshot_shape(api_client, active_menu):
    response = api_client.get('/api/v1/menus/')

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert_keys(data[0], {'id', 'title', 'slug', 'items'})
    assert data[0]['items']
    assert_keys(data[0]['items'][0], {'id', 'label', 'url', 'target', 'order', 'children'})
    assert data[0]['slug'] == active_menu.slug
