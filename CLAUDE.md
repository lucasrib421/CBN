# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CBN (Corrupção Brasileira News) is a journalism/news portal with a Django REST API backend and a React frontend. Authentication is handled via Keycloak (OIDC). The project is fully Dockerized.

## Development Commands

All commands run through a Makefile wrapping Docker Compose. Always prefer `make` commands over raw `docker compose` commands.

### Essential Commands

```bash
make setup           # First-time setup: builds, migrates, seeds data
make up              # Start all services
make down            # Stop all services
make restart         # Restart all services
make restart-api     # Restart Django only
make restart-front   # Restart React only
make check           # Health check all services
make status          # Show container status + URLs
```

### Backend (Django)

```bash
make migrate         # Apply migrations
make makemigrations  # Create migrations after model changes
make seed            # Load initial data (Status, Categories, Tags, Roles, Menu)
make superuser       # Create admin user
make shell           # Django interactive shell
make dbshell         # psql connected to cbn_db
make api-bash        # Bash shell inside API container
make docs            # Open Swagger UI in browser
```

### Frontend (React)

```bash
make lint                        # Run ESLint
make npm-install PKG=package     # Install npm dependency (stops containers, installs, rebuilds)
make npm-install-dev PKG=package # Install npm devDependency
make front-bash                  # Shell inside frontend container
```

### Logs

```bash
make logs            # All services (live)
make logs-api        # Django logs
make logs-front      # Frontend logs
make logs-db         # PostgreSQL logs
make logs-kc         # Keycloak logs
```

### Cleanup

```bash
make clean           # Stop + remove volumes (DELETES database!)
make reset           # Full reset: clean + rebuild + migrate + seed
```

## Architecture

### Backend (Django 6.0 + DRF)

**Django settings module:** `core.settings`

**Three Django apps:**
- **`setup`** — Contains ALL models (the data layer). Every model lives here: `Media`, `Status`, `Category`, `Tag`, `Role`, `Author`, `Post`, `HomeSection`, `HomeSectionItem`, `Menu`, `MenuItem`, `Redirect`. All models are registered in `setup/admin.py`. This app has no views of its own (empty `urls.py`). Fixtures live in `setup/fixtures/initial_data.json`.
- **`homeNews`** — Public read-only API. Uses `ReadOnlyModelViewSet` for posts, categories, tags, home sections, and menus. Posts are looked up by slug, filtered to `status__name='PUBLISHED'` only. Has custom `PostFilter` for filtering by title, category slug, tag slug, and author name.
- **`painelControle`** — Admin/authenticated API (work in progress). Uses a `BaseViewSet` with dynamic permissions (AllowAny for list/retrieve, IsAuthenticated for create, IsAdminUser for destroy). Currently only `MediaViewSet` is implemented.

**API URL structure:**
- `/admin/` — Django admin
- `/api/` — Public API (homeNews app): `/api/posts/`, `/api/categories/`, `/api/tags/`, `/api/home/`, `/api/menus/`
- `/api/schema/` — OpenAPI schema (drf-spectacular)
- `/api/schema/swagger/` — Swagger UI
- `/api/schema/redoc/` — ReDoc
- `/setup-rotas/` — Setup app routes (currently empty)

**Key pattern:** Models are defined in `setup` but serializers and views are in `homeNews` (public) and `painelControle` (admin). Both apps import models from `setup.models`.

**Authentication:** Keycloak issues JWTs validated by `djangorestframework-simplejwt` using RS256. The `preferred_username` claim maps to Django's `User.username`. Authors must exist in both Keycloak and Django (linked via `Author.user` OneToOneField to `django.contrib.auth.User`).

**Serializer pattern:** `homeNews` uses two serializers for posts — `PostListSerializer` (lightweight, no content field) for list views and `PostDetailSerializer` (full) for detail views. `painelControle` serializers use separate read-only `_info` fields and write-only FK fields.

**Seed data:** `setup/fixtures/initial_data.json` contains initial Status (DRAFT, PUBLISHED, ARCHIVED), Categories, Tags, Roles, and Menu data. Load with `make seed`.

### Frontend (React 19 + TypeScript + Vite + TailwindCSS)

**Entry point:** `frontend/src/main.tsx` wraps the app in `AuthProvider` (react-oidc-context) and `BrowserRouter`.

**Path alias:** `@/` maps to `src/`. Configured in both `tsconfig.app.json` and `vite.config.ts`. Always use `@/` imports instead of relative paths:
```tsx
import { api } from '@/services/api'       // Good
import { api } from '../../../services/api' // Avoid
```

**Structure:**
- `src/types/index.tsx` — TypeScript interfaces mirroring the DRF serializers
- `src/services/api.ts` — Axios instance pointing to `http://localhost:8000/api`
- `src/services/newsService.ts` — API call functions (home data, menus, posts)
- `src/pages/HomeNews/` — Public site pages
- `src/pages/PainelControle/` — Admin panel pages (Keycloak-protected)
- `src/components/` — Shared components (Header)
- `src/routes/index.tsx` — Route definitions (currently not used; App.tsx defines its own routes)

**Environment variables** (prefixed with `VITE_`): `VITE_API_URL`, `VITE_KEYCLOAK_URL`, `VITE_KEYCLOAK_REALM`, `VITE_KEYCLOAK_CLIENT_ID`

**HMR:** Vite is configured with polling and explicit HMR settings for Docker compatibility in `vite.config.ts`.

### Infrastructure

- **Dev:** `docker-compose.yml` — Postgres (port 5433 on host), Keycloak (port 8080), Django dev server (port 8000), Vite dev server (port 5173). Postgres init script (`docker/postgres/init_db.sh`) auto-creates the `keycloak` database. All services wait for Postgres healthcheck before starting.
- **Prod:** `docker-compose.prod.yml` — Adds Traefik for SSL/reverse proxy, uses Gunicorn, Nginx for frontend.
- **Database:** PostgreSQL 15. Django uses `cbn_db`, Keycloak uses `keycloak` — both on the same Postgres instance.

## Environment Setup

Copy `.env.example` to `.env` (or just run `make setup`). Key variables: `SECRET_KEY`, `DEBUG`, `POSTGRES_*`, `KEYCLOAK_ADMIN`, `KEYCLOAK_ADMIN_PASSWORD`. Frontend env vars go in `frontend/.env`.

## Conventions

- The project language is Portuguese (Brazilian). Models, comments, and UI text are in Portuguese.
- Locale is `pt-br`, timezone is `America/Sao_Paulo`.
- Models use explicit `db_table` names (lowercase, snake_case).
- Author primary keys are UUIDs; other models use auto-incrementing integers.
- Slugs are used for URL lookups on Posts, Categories, Tags, and Menus.
- Frontend uses `@/` path aliases for imports (never relative paths like `../../`).
- `.editorconfig` enforces: 2-space indent for TS/JS/JSON/YAML, 4-space for Python, tabs for Makefile.
