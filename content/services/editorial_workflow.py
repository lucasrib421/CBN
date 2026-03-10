from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone

from accounts.models import Role
from accounts.services.editorial_roles import ResolvedEditorialRole
from content.models import Post, PostStatus, PostStatusTransition


@dataclass(frozen=True)
class TransitionCheckResult:
    normalized_published_at: datetime | None
    should_audit: bool


class EditorialWorkflowError(Exception):
    pass


class InvalidEditorialTransitionError(EditorialWorkflowError):
    pass


class EditorialPermissionDeniedError(EditorialWorkflowError):
    pass


class EditorialWorkflowService:
    _BASE_TRANSITIONS = {
        PostStatus.DRAFT: (PostStatus.REVIEW, PostStatus.PUBLISHED, PostStatus.ARCHIVED),
        PostStatus.REVIEW: (PostStatus.DRAFT, PostStatus.PUBLISHED, PostStatus.ARCHIVED),
        PostStatus.PUBLISHED: (PostStatus.DRAFT, PostStatus.ARCHIVED),
        PostStatus.ARCHIVED: (PostStatus.DRAFT,),
    }

    def allowed_transitions(
        self,
        *,
        current_status: str,
        actor: ResolvedEditorialRole,
    ) -> tuple[str, ...]:
        if current_status not in self._BASE_TRANSITIONS:
            raise InvalidEditorialTransitionError(
                f'Estado inválido para workflow: {current_status}'
            )

        base_targets = self._BASE_TRANSITIONS[current_status]
        if actor.can_publish_directly:
            return base_targets

        if current_status == PostStatus.PUBLISHED:
            return tuple()

        return tuple(target for target in base_targets if target != PostStatus.PUBLISHED)

    def validate_transition(
        self,
        *,
        current_status: str,
        target_status: str,
        published_at: datetime | None,
        actor: ResolvedEditorialRole,
        published_at_changed: bool,
    ) -> TransitionCheckResult:
        if target_status not in PostStatus.values:
            raise InvalidEditorialTransitionError(f'Status alvo inválido: {target_status}')

        if current_status not in PostStatus.values:
            raise InvalidEditorialTransitionError(f'Status atual inválido: {current_status}')

        status_changed = current_status != target_status
        if status_changed:
            allowed = self.allowed_transitions(current_status=current_status, actor=actor)
            if target_status not in allowed:
                raise InvalidEditorialTransitionError(
                    f'Transição não permitida: {current_status} -> {target_status}.'
                )

        if (
            published_at_changed
            and target_status != PostStatus.PUBLISHED
            and published_at is not None
        ):
            raise InvalidEditorialTransitionError(
                'O campo published_at só pode ser definido para posts publicados.'
            )

        transition_touches_publication = (
            current_status == PostStatus.PUBLISHED or target_status == PostStatus.PUBLISHED
        )
        if transition_touches_publication and not actor.can_publish_directly:
            raise EditorialPermissionDeniedError(
                'Você não possui permissão para alterar estado de publicação.'
            )

        if (
            published_at_changed
            and target_status == PostStatus.PUBLISHED
            and not actor.can_publish_directly
        ):
            raise EditorialPermissionDeniedError(
                'Você não possui permissão para alterar agendamento de publicação.'
            )

        normalized_published_at = self._normalize_published_at(
            target_status=target_status,
            published_at=published_at,
        )
        return TransitionCheckResult(
            normalized_published_at=normalized_published_at,
            should_audit=status_changed,
        )

    def _normalize_published_at(
        self,
        *,
        target_status: str,
        published_at: datetime | None,
    ) -> datetime | None:
        if target_status != PostStatus.PUBLISHED:
            return None
        if published_at is None:
            return timezone.now()
        return published_at

    def record_transition(
        self,
        *,
        post: Post,
        from_status: str,
        to_status: str,
        user: User | None,
        actor_role: Role | None,
    ) -> PostStatusTransition:
        return PostStatusTransition.objects.create(
            post=post,
            from_status=from_status,
            to_status=to_status,
            changed_by=user,
            actor_role=actor_role,
            published_at_snapshot=post.published_at,
        )

    @classmethod
    def all_statuses(cls) -> tuple[str, ...]:
        return tuple(PostStatus.values)

    @classmethod
    def as_label_map(cls) -> dict[str, str]:
        return dict(PostStatus.choices)


def get_default_editorial_workflow_service() -> EditorialWorkflowService:
    return EditorialWorkflowService()
