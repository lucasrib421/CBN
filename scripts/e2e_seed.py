#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


KEYCLOAK_BASE_URL = os.getenv('E2E_KEYCLOAK_URL', 'http://localhost:8080')
KEYCLOAK_REALM = os.getenv('E2E_KEYCLOAK_REALM', 'cbn')
KEYCLOAK_ADMIN_USER = os.getenv('KEYCLOAK_ADMIN', 'admin')
KEYCLOAK_ADMIN_PASSWORD = os.getenv('KEYCLOAK_ADMIN_PASSWORD', 'admin')
E2E_EDITOR_USERNAME = os.getenv('E2E_EDITOR_USERNAME', 'e2e_editor')
E2E_EDITOR_PASSWORD = os.getenv('E2E_EDITOR_PASSWORD', 'e2e-editor-123')


def wait_for_http(url: str, timeout_seconds: int = 120) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.status < 500:
                    return
        except Exception as exc:  # pragma: no cover - defensive for setup script
            last_error = exc
        time.sleep(1)
    raise RuntimeError(f'Could not reach {url}. Last error: {last_error}')


def http_json(
    method: str,
    url: str,
    token: str | None = None,
    payload: dict | list | None = None,
) -> tuple[int, bytes]:
    data = None
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    if token:
        headers['Authorization'] = f'Bearer {token}'

    request = urllib.request.Request(url=url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:  # pragma: no cover - defensive for setup script
        body = exc.read()
        raise RuntimeError(f'HTTP {exc.code} for {method} {url}: {body.decode("utf-8", "ignore")}')


def get_keycloak_admin_token() -> str:
    token_url = f'{KEYCLOAK_BASE_URL}/realms/master/protocol/openid-connect/token'
    form_data = urllib.parse.urlencode(
        {
            'grant_type': 'password',
            'client_id': 'admin-cli',
            'username': KEYCLOAK_ADMIN_USER,
            'password': KEYCLOAK_ADMIN_PASSWORD,
        }
    ).encode('utf-8')
    request = urllib.request.Request(
        token_url,
        data=form_data,
        method='POST',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.loads(response.read().decode('utf-8'))
    return data['access_token']


def ensure_keycloak_user() -> None:
    token = get_keycloak_admin_token()
    query = urllib.parse.quote(E2E_EDITOR_USERNAME)
    users_url = f'{KEYCLOAK_BASE_URL}/admin/realms/{KEYCLOAK_REALM}/users?username={query}'
    _, raw_users = http_json('GET', users_url, token=token)
    users = json.loads(raw_users.decode('utf-8'))

    if users:
        user_id = users[0]['id']
    else:
        create_payload = {
            'username': E2E_EDITOR_USERNAME,
            'enabled': True,
            'firstName': 'E2E',
            'lastName': 'Editor',
            'email': f'{E2E_EDITOR_USERNAME}@example.com',
            'emailVerified': True,
            'requiredActions': [],
        }
        create_url = f'{KEYCLOAK_BASE_URL}/admin/realms/{KEYCLOAK_REALM}/users'
        http_json('POST', create_url, token=token, payload=create_payload)
        _, raw_users = http_json('GET', users_url, token=token)
        users = json.loads(raw_users.decode('utf-8'))
        if not users:
            raise RuntimeError('Failed to create Keycloak e2e user.')
        user_id = users[0]['id']

    update_url = f'{KEYCLOAK_BASE_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user_id}'
    http_json(
        'PUT',
        update_url,
        token=token,
        payload={
            'username': E2E_EDITOR_USERNAME,
            'enabled': True,
            'firstName': 'E2E',
            'lastName': 'Editor',
            'email': f'{E2E_EDITOR_USERNAME}@example.com',
            'emailVerified': True,
            'requiredActions': [],
        },
    )

    reset_password_url = (
        f'{KEYCLOAK_BASE_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user_id}/reset-password'
    )
    http_json(
        'PUT',
        reset_password_url,
        token=token,
        payload={
            'type': 'password',
            'value': E2E_EDITOR_PASSWORD,
            'temporary': False,
        },
    )


def ensure_django_entities() -> None:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    os.environ.setdefault('POSTGRES_HOST', 'localhost')
    os.environ.setdefault('POSTGRES_PORT', '5433')
    os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/1')

    import django

    django.setup()

    from django.contrib.auth.models import User

    from accounts.models import Author
    from content.models import Category, Tag

    user, created = User.objects.get_or_create(
        username=E2E_EDITOR_USERNAME,
        defaults={
            'email': f'{E2E_EDITOR_USERNAME}@example.com',
            'is_active': True,
        },
    )
    if created:
        user.set_password('unused-local-password')
        user.save(update_fields=['password'])

    Author.objects.get_or_create(
        user=user,
        defaults={
            'name': 'E2E Editor',
            'bio': 'Perfil de autor para testes E2E.',
        },
    )

    Category.objects.get_or_create(
        slug='e2e-categoria',
        defaults={
            'name': 'E2E Categoria',
            'color': '#1D4ED8',
            'is_active': True,
        },
    )
    Tag.objects.get_or_create(
        slug='e2e-tag',
        defaults={
            'name': 'E2E Tag',
        },
    )


def main() -> None:
    wait_for_http(f'{KEYCLOAK_BASE_URL}/realms/master/.well-known/openid-configuration')
    ensure_keycloak_user()
    ensure_django_entities()
    print('E2E seed completed: keycloak user + django user/author/category/tag ready.')


if __name__ == '__main__':
    main()
