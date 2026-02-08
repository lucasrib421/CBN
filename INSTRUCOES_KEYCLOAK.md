# Configuracao do Keycloak (Autenticacao)

O ambiente local ja sobe com realm importado automaticamente.

## 1. Subir ambiente

```bash
make setup
```

Ou, se ja estiver configurado:

```bash
make up
```

## 2. Como o import funciona

- O `docker-compose.yml` inicia o Keycloak com `start-dev --import-realm`
- O arquivo `docker/keycloak/cbn-realm-export.json` e montado em `/opt/keycloak/data/import/cbn-realm-export.json`
- O realm importado e `cbn`
- O client esperado pelo frontend e `cbn-frontend`

## 3. Acesso ao painel

- URL: `http://localhost:8080`
- Admin user/password: `KEYCLOAK_ADMIN` e `KEYCLOAK_ADMIN_PASSWORD` do `.env`

## 4. Dados esperados no frontend

As variaveis em `frontend/.env` (ou no ambiente do container) devem apontar para:

- `VITE_KEYCLOAK_URL=http://localhost:8080`
- `VITE_KEYCLOAK_REALM=cbn`
- `VITE_KEYCLOAK_CLIENT_ID=cbn-frontend`

## 5. Vinculo com Django (obrigatorio para autores)

Para um usuario autenticado no Keycloak conseguir atuar como autor no Django:

1. Acesse `http://localhost:8000/admin`
2. Crie um `User` com o mesmo `username` do Keycloak
3. Em `Autores`, crie um `Author` vinculado a esse `User`

## 6. Troubleshooting rapido

Se o Keycloak nao subir por banco ausente (ambiente antigo sem init):

```bash
docker compose exec db psql -U postgres -d postgres -c "CREATE DATABASE keycloak"
docker compose restart keycloak
```
