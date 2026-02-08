import pytest

from homeNews.tests.helpers import assert_keys
from setup.tests.factories import TagFactory


pytestmark = pytest.mark.django_db


def test_tags_snapshot_shape(api_client):
    TagFactory(name='Corrupção', slug='corrupcao')

    response = api_client.get('/api/tags/')

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert_keys(data[0], {'id', 'name', 'slug'})
