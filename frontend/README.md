# Frontend CBN

Aplicacao React + TypeScript + Vite do projeto CBN.

## Stack

- React 19
- TypeScript
- Vite
- Tailwind CSS
- react-oidc-context (login via Keycloak)
- Vitest + Testing Library (testes)

## Variaveis de ambiente

O frontend usa as variaveis abaixo:

- `VITE_API_URL`
- `VITE_KEYCLOAK_URL`
- `VITE_KEYCLOAK_REALM`
- `VITE_KEYCLOAK_CLIENT_ID`

No ambiente Docker de desenvolvimento, elas sao definidas via `docker-compose.yml` e `frontend/.env`.

## Comandos principais

Execute no container `frontend`:

```bash
docker compose exec frontend npm run lint
docker compose exec frontend npm run test
docker compose exec frontend npm run build
```

## Integracao com API

O cliente Axios usa `VITE_API_URL` e aponta para `/api`.

Exemplo local:

- API base efetiva: `http://localhost:8000/api`

## CI

No GitHub Actions, o job `frontend` executa:

1. `npm ci`
2. `npm run lint`
3. `npm run test`
4. `npm run build`
