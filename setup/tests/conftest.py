import pytest

from setup.tests.factories import PostFactory


@pytest.fixture
def published_post(db):
    return PostFactory()
