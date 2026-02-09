import pytest


@pytest.fixture(autouse=True)
def _disable_ssl_redirect(settings):
    settings.SECURE_SSL_REDIRECT = False


@pytest.fixture
def api_base_url() -> str:
    return '/api/v1/'
