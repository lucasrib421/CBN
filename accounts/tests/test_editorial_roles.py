import pytest
from django.contrib.auth.models import User

from accounts.models import Author, Role
from accounts.services.editorial_roles import (
    EDITOR_IN_CHIEF_ROLE_SLUG,
    REPORTER_ROLE_SLUG,
    resolve_editorial_role,
)


pytestmark = pytest.mark.django_db


def _seed_roles() -> None:
    Role.objects.get_or_create(
        slug=EDITOR_IN_CHIEF_ROLE_SLUG,
        defaults={
            'name': 'Editor Chefe',
            'description': 'Aprovação final de publicações',
        },
    )
    Role.objects.get_or_create(
        slug=REPORTER_ROLE_SLUG,
        defaults={
            'name': 'Repórter',
            'description': 'Produz conteúdo editorial',
        },
    )


def test_resolve_editorial_role_prioritizes_claim_mapping():
    _seed_roles()
    user = User.objects.create_user(username='editor-claims', password='secret')

    mapped = resolve_editorial_role(
        user=user,
        token_payload={'realm_access': {'roles': ['editor']}},
    )

    assert mapped.role is not None
    assert mapped.role.slug == EDITOR_IN_CHIEF_ROLE_SLUG
    assert mapped.source == 'claims'
    assert mapped.can_publish_directly is True


def test_resolve_editorial_role_falls_back_to_author_role():
    _seed_roles()
    user = User.objects.create_user(username='reporter-author', password='secret')
    reporter = Role.objects.get(slug=REPORTER_ROLE_SLUG)
    Author.objects.create(user=user, name='Repórter Local', role=reporter)

    mapped = resolve_editorial_role(user=user, token_payload=None)

    assert mapped.role is not None
    assert mapped.role.slug == REPORTER_ROLE_SLUG
    assert mapped.source == 'author'
    assert mapped.can_publish_directly is False
