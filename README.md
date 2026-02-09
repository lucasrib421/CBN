# CBN - Corrupção Brasileira News

Portal jornalístico com Django REST API (backend) e Next.js (frontend). Autenticação via Keycloak (OIDC). Projeto 100% Dockerizado.

## Tecnologias

| Camada | Stack |
|--------|-------|
| **Backend** | Python 3.12, Django 6.0, Django REST Framework, drf-spectacular |
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS 4, Auth.js v5 |
| **Banco de Dados** | PostgreSQL 15 |
| **Cache** | Redis 7 |
| **Autenticação** | Keycloak 26 (OIDC / JWT RS256) + Auth.js v5 |
| **Infra Dev** | Docker Compose, Makefile |
| **Infra Prod** | Traefik (SSL), Gunicorn, Nginx |
| **CI/CD** | GitHub Actions (lint, test, build, security) |

## Quick Start

**Requisitos:** [Git](https://git-scm.com/) + [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
git clone https://github.com/GabrielDavi7/CBN.git
cd CBN
make setup
```

O `make setup` faz tudo automaticamente:
1. Cria os arquivos `.env` a partir do `.env.example`
2. Builda as imagens Docker
3. Sobe todos os containers
4. Roda as migrations do Django
5. Carrega dados iniciais (categorias, tags, status, roles, menu)
6. Importa o realm `cbn` no Keycloak a partir de `docker/keycloak/cbn-realm-export.json`

Depois do setup, crie um superusuário:

```bash
make superuser
```

## URLs do Ambiente Local

| Serviço | URL |
|---------|-----|
| Frontend (Next.js) | http://localhost:3000 |
| Admin Panel | http://localhost:3000/admin |
| API (Django) | http://localhost:8000/api/v1/ |
| Django Admin | http://localhost:8000/admin/ |
| Swagger UI | http://localhost:8000/api/schema/swagger/ |
| ReDoc | http://localhost:8000/api/schema/redoc/ |
| Keycloak | http://localhost:8080 |

## Comandos do Makefile

Rode `make help` para ver todos os comandos. Os mais usados:

### Ciclo de Vida

```bash
make up              # Sobe todos os containers
make down            # Para todos os containers
make restart         # Reinicia tudo
make restart-api     # Reinicia apenas a API
make restart-front   # Reinicia apenas o frontend
make build           # Builda as imagens
make rebuild         # Rebuilda sem cache e sobe
```

### Django

```bash
make migrate         # Roda as migrations
make makemigrations  # Cria novas migrations
make seed            # Carrega dados iniciais
make superuser       # Cria superusuário
make shell           # Shell interativo do Django
make collectstatic   # Coleta arquivos estáticos
```

### Frontend

```bash
make lint                        # Roda ESLint
make npm-install PKG=axios       # Instala dependência
make npm-install-dev PKG=vitest  # Instala devDependência
```

## Testes e Qualidade

### Backend (dentro do container API)

```bash
docker compose exec api pytest
docker compose exec api pytest --cov
docker compose exec api ruff check core content accounts media_app navigation home homeNews painelControle conftest.py manage.py
docker compose exec api ruff format --check core content accounts media_app navigation home homeNews painelControle conftest.py manage.py
docker compose exec -e HOME=/tmp api pip-audit
```

### Frontend (dentro do container frontend)

```bash
docker compose exec frontend npm run lint
docker compose exec frontend npm run test
docker compose exec frontend npm run build
docker compose exec frontend npm audit --audit-level=high
```

## CI/CD

Pipeline GitHub Actions em `.github/workflows/ci.yml` com 3 jobs paralelos:

- `backend`: `manage.py check --deploy`, `pytest --cov`, `ruff check`, `ruff format --check` (com PostgreSQL e Redis)
- `frontend`: `npm run lint`, `npm run test`, `npm run build`
- `security`: `pip-audit` e `npm audit --audit-level=high`

Triggers:
- push para `dev` e `main`
- pull request para `main`

Atualizações automáticas de dependências em `.github/dependabot.yml` (pip, npm e GitHub Actions, semanal).

### Logs e Debug

```bash
make logs            # Logs de todos os serviços (ao vivo)
make logs-api        # Logs da API
make logs-front      # Logs do frontend
make logs-db         # Logs do PostgreSQL
make logs-kc         # Logs do Keycloak
make status          # Status dos containers + URLs
make check           # Health check de todos os serviços
make docs            # Abre Swagger UI no navegador
```

### Acesso Direto aos Containers

```bash
make api-bash        # Terminal bash na API
make front-bash      # Terminal sh no frontend
make dbshell         # psql conectado ao banco
```

### Limpeza

```bash
make clean           # Para tudo e remove volumes (APAGA dados!)
make reset           # Reset completo: limpa, rebuilda, migrate + seed
```

## Arquitetura

### Backend — Django Domain Apps

O backend é dividido em 5 domain apps + 2 apps de API:

| App | Modelos | Responsabilidade |
|-----|---------|------------------|
| `content` | Post, Category, Tag, PostStatus | Conteúdo editorial |
| `accounts` | Author, Role | Autores e papéis |
| `media_app` | Media | Upload e gerenciamento de mídia |
| `navigation` | Menu, MenuItem, Redirect | Navegação e redirects SEO |
| `home` | HomeSection, HomeSectionItem | Layout da home page |
| `homeNews` | — (views/serializers) | API pública read-only v1 |
| `painelControle` | — (views/serializers) | API admin autenticada v1 |

### Frontend — Next.js 16

| Rota | Tipo | Descrição |
|------|------|-----------|
| `/` | SSR | Home page com seções |
| `/[slug]` | SSR | Detalhe do post |
| `/categoria/[slug]` | SSR | Posts por categoria |
| `/admin` | Protegido | Dashboard com estatísticas |
| `/admin/posts` | Protegido | Lista de publicações |
| `/admin/posts/new` | Protegido | Criar publicação |
| `/admin/posts/[id]/edit` | Protegido | Editar publicação |
| `/admin/media` | Protegido | Biblioteca de mídia |
| `/admin/categories` | Protegido | CRUD de categorias |
| `/admin/home-sections` | Protegido | Editor de seções da home |

Autenticação do admin via Auth.js v5 + Keycloak (client confidencial).

### Infraestrutura

- **Dev:** `docker-compose.yml` — Postgres (porta 5433 no host), Keycloak (8080), Django (8000), Next.js (3000), Redis (6379)
- **Prod:** `docker-compose.prod.yml` — Traefik para SSL/reverse proxy, Gunicorn, Nginx para frontend
- **Cache:** Redis 7 — cache de endpoints públicos com invalidação via signals
- **Database:** PostgreSQL 15. Django usa `cbn_db`, Keycloak usa `keycloak` — ambos na mesma instância

## Estrutura do Projeto

```
CBN/
├── core/                  # Configurações Django (settings, urls, wsgi)
├── content/               # App: Post, Category, Tag, PostStatus
├── accounts/              # App: Author, Role
├── media_app/             # App: Media
├── navigation/            # App: Menu, MenuItem, Redirect
├── home/                  # App: HomeSection, HomeSectionItem
├── homeNews/              # API pública (read-only, versionada v1)
├── painelControle/        # API admin (autenticada, CRUD completo)
├── frontend/              # Next.js 16 + TypeScript + Tailwind CSS 4
│   ├── src/
│   │   ├── app/           # App Router (pages, layouts)
│   │   │   ├── admin/     # Painel admin (protegido)
│   │   │   └── api/auth/  # Auth.js route handler
│   │   ├── components/    # Componentes reutilizáveis
│   │   ├── lib/           # API clients, utilitários
│   │   ├── types/         # Interfaces TypeScript
│   │   └── auth.ts        # Auth.js v5 config (Keycloak)
│   └── middleware.ts       # Proteção de rotas /admin/*
├── docker/
│   ├── keycloak/          # Realm export + README
│   └── postgres/          # Script de init do banco
├── .github/
│   ├── workflows/ci.yml   # Pipeline CI (lint, test, build, security)
│   └── dependabot.yml     # Atualizações automáticas
├── docker-compose.yml     # Ambiente de desenvolvimento
├── docker-compose.prod.yml # Ambiente de produção
├── Dockerfile             # Imagem da API Django
├── Makefile               # Comandos de desenvolvimento
└── .env.example           # Template de variáveis de ambiente
```

## API

A API segue o padrão REST com Django REST Framework, versionada em `/api/v1/`.

**Endpoints Públicos** (`/api/v1/`):
- `GET /api/v1/posts/` — Lista de posts publicados (paginada, filtros: titulo, categoria, tag, autor)
- `GET /api/v1/posts/{slug}/` — Detalhe de um post
- `GET /api/v1/categories/` — Categorias
- `GET /api/v1/tags/` — Tags
- `GET /api/v1/home/` — Seções da home
- `GET /api/v1/menus/` — Menus de navegação
- `GET /api/v1/redirects/` — Redirects SEO

Todos os endpoints públicos possuem:
- Paginação (`PageNumberPagination`, 20 por página)
- Rate limiting (anônimo: 100/hora, autenticado: 1000/hora)
- Cache headers (`Cache-Control`, `ETag`)

**Endpoints Admin** (`/api/v1/painel/`):
- CRUD completo para: Posts, Categories, Tags, Media, HomeSections, HomeSectionItems, Menus, MenuItems
- Autenticação via JWT (Keycloak)

**Documentação interativa:** Swagger UI em http://localhost:8000/api/schema/swagger/

## Dados Iniciais (Seed)

O comando `make seed` carrega dados iniciais para desenvolvimento:

- **Categorias:** Politica, Economia, Judiciario, Investigacoes, Internacional
- **Tags:** Corrupcao, Lavagem de Dinheiro, Licitacao, Congresso, STF
- **Roles:** Editor Chefe, Reporter, Colunista
- **Menu:** Menu Principal com 5 itens

## Conexao Externa ao Banco

Para conectar DBeaver, PGAdmin ou outra ferramenta:

| Campo | Valor |
|-------|-------|
| Host | `localhost` |
| Porta | `5433` (nao `5432`) |
| Usuario | `postgres` |
| Senha | `postgres` |
| Banco | `cbn_db` |

## Deploy (Producao)

O ambiente de producao usa `docker-compose.prod.yml` com Traefik (SSL automatico via Let's Encrypt), Gunicorn e Nginx. Nao use este arquivo localmente.

## Keycloak

- Realm versionado: `docker/keycloak/cbn-realm-export.json`
- Compose de desenvolvimento sobe o Keycloak com `start-dev --import-realm`
- Client: `cbn-frontend` (confidential, requer secret)
- Consulte `docker/keycloak/README.md` para detalhes do realm e do import automatico
