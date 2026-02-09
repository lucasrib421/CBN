# Keycloak realm CBN

Arquivo versionado de importacao: `cbn-realm-export.json`.

## Realm

- Nome: `cbn`
- Habilitado: `true`

## Cliente OIDC

- Client ID: `cbn-frontend`
- Tipo: confidential client (client secret required)
- Client Secret (dev): `cbn-dev-secret-change-in-production`
- Fluxo: Authorization Code
- Redirect URIs:
  - `http://localhost:3000/*`
  - `http://localhost:3000/api/auth/callback/keycloak`
- Web origins:
  - `http://localhost:3000`

## Roles de realm

- `admin`
- `editor`

## Como funciona no compose

O servico `keycloak` no `docker-compose.yml` inicia com `start-dev --import-realm`
e monta este arquivo em `/opt/keycloak/data/import/cbn-realm-export.json`.
No bootstrap do ambiente, o Keycloak importa o realm `cbn` automaticamente.

## Atualizar o export do realm

Quando houver mudancas no realm feitas pelo painel do Keycloak, atualize o arquivo versionado:

```bash
docker compose exec keycloak /opt/keycloak/bin/kc.sh export --dir /tmp/export --realm cbn
docker compose cp keycloak:/tmp/export/cbn-realm.json docker/keycloak/cbn-realm-export.json
```

Depois, valide o JSON e commit as alteracoes.
