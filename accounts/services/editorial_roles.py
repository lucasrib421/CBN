from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Any, Mapping

from django.contrib.auth.models import User

from accounts.models import Role


EDITOR_IN_CHIEF_ROLE_SLUG = 'editor-chefe'
REPORTER_ROLE_SLUG = 'reporter'
COLUMNIST_ROLE_SLUG = 'colunista'

_ROLE_PRECEDENCE = {
    EDITOR_IN_CHIEF_ROLE_SLUG: 30,
    REPORTER_ROLE_SLUG: 20,
    COLUMNIST_ROLE_SLUG: 10,
}

_CLAIM_ROLE_ALIASES = {
    'admin': EDITOR_IN_CHIEF_ROLE_SLUG,
    'editor': EDITOR_IN_CHIEF_ROLE_SLUG,
    'editor-chefe': EDITOR_IN_CHIEF_ROLE_SLUG,
    'editor-chefe-cbn': EDITOR_IN_CHIEF_ROLE_SLUG,
    'editor-chief': EDITOR_IN_CHIEF_ROLE_SLUG,
    'editor-in-chief': EDITOR_IN_CHIEF_ROLE_SLUG,
    'reporter': REPORTER_ROLE_SLUG,
    'reporter-cbn': REPORTER_ROLE_SLUG,
    'colunista': COLUMNIST_ROLE_SLUG,
    'columnist': COLUMNIST_ROLE_SLUG,
}


@dataclass(frozen=True)
class ResolvedEditorialRole:
    role: Role | None
    source: str
    claim_role_slugs: tuple[str, ...]
    is_staff_override: bool = False

    @property
    def can_publish_directly(self) -> bool:
        if self.is_staff_override:
            return True
        if self.role is None:
            return False
        return self.role.slug == EDITOR_IN_CHIEF_ROLE_SLUG


def _normalize_role_name(raw_role: str) -> str:
    normalized = unicodedata.normalize('NFKD', raw_role).encode('ascii', 'ignore').decode('ascii')
    normalized = normalized.strip().lower().replace('_', '-').replace(' ', '-')
    while '--' in normalized:
        normalized = normalized.replace('--', '-')
    return normalized


def _extract_claim_roles(token_payload: Mapping[str, Any] | None) -> set[str]:
    if not token_payload:
        return set()

    claim_roles: set[str] = set()

    realm_access = token_payload.get('realm_access')
    if isinstance(realm_access, dict):
        roles = realm_access.get('roles')
        if isinstance(roles, list):
            for role in roles:
                if isinstance(role, str):
                    claim_roles.add(_normalize_role_name(role))

    resource_access = token_payload.get('resource_access')
    if isinstance(resource_access, dict):
        for client_claims in resource_access.values():
            if not isinstance(client_claims, dict):
                continue
            client_roles = client_claims.get('roles')
            if not isinstance(client_roles, list):
                continue
            for role in client_roles:
                if isinstance(role, str):
                    claim_roles.add(_normalize_role_name(role))

    return claim_roles


def _select_highest_precedence_role(roles: list[Role]) -> Role | None:
    if not roles:
        return None

    return sorted(
        roles,
        key=lambda role: _ROLE_PRECEDENCE.get(role.slug, 0),
        reverse=True,
    )[0]


def resolve_editorial_role(
    *,
    user: User | None,
    token_payload: Mapping[str, Any] | None = None,
) -> ResolvedEditorialRole:
    claim_roles = _extract_claim_roles(token_payload)
    mapped_slugs = sorted(
        {_CLAIM_ROLE_ALIASES[role] for role in claim_roles if role in _CLAIM_ROLE_ALIASES}
    )

    if user is not None and (user.is_staff or user.is_superuser):
        staff_role = Role.objects.filter(slug=EDITOR_IN_CHIEF_ROLE_SLUG).first()
        return ResolvedEditorialRole(
            role=staff_role,
            source='staff',
            claim_role_slugs=tuple(mapped_slugs),
            is_staff_override=True,
        )

    if mapped_slugs:
        mapped_roles = list(Role.objects.filter(slug__in=mapped_slugs))
        mapped_role = _select_highest_precedence_role(mapped_roles)
        if mapped_role is not None:
            return ResolvedEditorialRole(
                role=mapped_role,
                source='claims',
                claim_role_slugs=tuple(mapped_slugs),
            )

    if user is not None:
        author_profile = getattr(user, 'author_profile', None)
        if author_profile and author_profile.role:
            return ResolvedEditorialRole(
                role=author_profile.role,
                source='author',
                claim_role_slugs=tuple(mapped_slugs),
            )

    return ResolvedEditorialRole(
        role=None,
        source='none',
        claim_role_slugs=tuple(mapped_slugs),
    )
