import pytest

from homeNews.tests.helpers import assert_keys


pytestmark = pytest.mark.django_db


def test_home_snapshot_shape(api_client, home_section_with_item):
    response = api_client.get('/api/home/')

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert_keys(data[0], {'id', 'title', 'section_type', 'order', 'items'})
    assert data[0]['items']
    assert_keys(data[0]['items'][0], {'id', 'order', 'post'})
