import pytest
from rest_framework.test import APIClient

from setup.tests.factories import (
    HomeSectionFactory,
    HomeSectionItemFactory,
    MenuFactory,
    MenuItemFactory,
    PostFactory,
)


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def public_post(db):
    return PostFactory()


@pytest.fixture
def home_section_with_item(db, public_post):
    section = HomeSectionFactory()
    HomeSectionItemFactory(section=section, post=public_post, order=1)
    return section


@pytest.fixture
def active_menu(db):
    menu = MenuFactory(title='Menu Principal', slug='menu-principal')
    MenuItemFactory(menu=menu, label='Política', url='/politica', order=1)
    return menu
