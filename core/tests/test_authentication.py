from __future__ import annotations

import pytest
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from core.authentication import KeycloakJWTAuthentication


class _FakeUntypedToken:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def __getitem__(self, item: str):
        return self.payload[item]


def test_ensure_access_token_accepts_simplejwt_access_token() -> None:
    token = _FakeUntypedToken({'token_type': 'access'})
    KeycloakJWTAuthentication._ensure_access_token(token)  # should not raise


def test_ensure_access_token_rejects_simplejwt_refresh_token() -> None:
    token = _FakeUntypedToken({'token_type': 'refresh'})

    with pytest.raises(InvalidToken):
        KeycloakJWTAuthentication._ensure_access_token(token)


def test_ensure_access_token_accepts_keycloak_bearer_token() -> None:
    token = _FakeUntypedToken({'typ': 'Bearer'})
    KeycloakJWTAuthentication._ensure_access_token(token)  # should not raise


def test_ensure_access_token_rejects_non_access_external_token() -> None:
    token = _FakeUntypedToken({'typ': 'Refresh'})

    with pytest.raises(InvalidToken):
        KeycloakJWTAuthentication._ensure_access_token(token)


def test_get_validated_token_returns_untyped_token_when_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = _FakeUntypedToken({'token_type': 'access'})
    monkeypatch.setattr('core.authentication.UntypedToken', lambda _raw: expected)

    token = KeycloakJWTAuthentication().get_validated_token('valid-token')

    assert token is expected


def test_get_validated_token_wraps_token_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise_token_error(_raw: str):
        raise TokenError('invalid-token')

    monkeypatch.setattr('core.authentication.UntypedToken', _raise_token_error)

    with pytest.raises(InvalidToken):
        KeycloakJWTAuthentication().get_validated_token('invalid-token')
