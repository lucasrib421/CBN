from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from accounts.models import Author, Role
from accounts.services.editorial_roles import resolve_editorial_role
from content.models import PostStatus
from content.services.editorial_workflow import (
    EditorialPermissionDeniedError,
    EditorialWorkflowService,
    InvalidEditorialTransitionError,
)


pytestmark = pytest.mark.django_db


def _seed_roles() -> tuple[Role, Role]:
    editor = Role.objects.create(name='Editor Chefe', slug='editor-chefe')
    reporter = Role.objects.create(name='Repórter', slug='reporter')
    return editor, reporter


def _actor(slug: str):
    user = User.objects.create_user(username=f'user-{slug}', password='secret')
    role = Role.objects.get(slug=slug)
    Author.objects.create(user=user, name=f'Autor {slug}', role=role)
    return resolve_editorial_role(user=user, token_payload=None)


def test_allowed_transitions_include_review_and_publish_for_editor():
    _seed_roles()
    service = EditorialWorkflowService()
    actor = _actor('editor-chefe')

    allowed = service.allowed_transitions(current_status=PostStatus.DRAFT, actor=actor)

    assert set(allowed) == {PostStatus.REVIEW, PostStatus.PUBLISHED, PostStatus.ARCHIVED}


def test_reporter_cannot_transition_directly_to_published():
    _seed_roles()
    service = EditorialWorkflowService()
    actor = _actor('reporter')

    with pytest.raises(InvalidEditorialTransitionError):
        service.validate_transition(
            current_status=PostStatus.DRAFT,
            target_status=PostStatus.PUBLISHED,
            published_at=None,
            actor=actor,
            published_at_changed=False,
        )


def test_publishing_without_datetime_defaults_to_now():
    _seed_roles()
    service = EditorialWorkflowService()
    actor = _actor('editor-chefe')

    result = service.validate_transition(
        current_status=PostStatus.REVIEW,
        target_status=PostStatus.PUBLISHED,
        published_at=None,
        actor=actor,
        published_at_changed=False,
    )

    assert result.normalized_published_at is not None
    assert abs((timezone.now() - result.normalized_published_at).total_seconds()) < 5


def test_reporter_cannot_edit_published_at_of_published_post():
    _seed_roles()
    service = EditorialWorkflowService()
    actor = _actor('reporter')

    with pytest.raises(EditorialPermissionDeniedError):
        service.validate_transition(
            current_status=PostStatus.PUBLISHED,
            target_status=PostStatus.PUBLISHED,
            published_at=timezone.now() + timedelta(days=1),
            actor=actor,
            published_at_changed=True,
        )
