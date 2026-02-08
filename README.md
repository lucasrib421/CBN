# CBN - Corrupção Brasileira News

Portal jornalístico com Django REST API (backend) e React (frontend). Autenticação via Keycloak (OIDC). Projeto 100% Dockerizado.

## Tecnologias

| Camada | Stack |
|--------|-------|
| **Backend** | Python 3.12, Django 6.0, Django REST Framework, drf-spectacular |
| **Frontend** | React 19, TypeScript, Vite, TailwindCSS |
| **Banco de Dados** | PostgreSQL 15 |
| **Autenticação** | Keycloak 26 (OIDC / JWT RS256) |
| **Infra Dev** | Docker Compose, Makefile |
| **Infra Prod** | Traefik (SSL), Gunicorn, Nginx |

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

Depois do setup, crie um superusuário:

```bash
make superuser
```

## URLs do Ambiente Local

| Serviço | URL |
|---------|-----|
| Frontend (React) | http://localhost:5173 |
| API (Django) | http://localhost:8000/api/ |
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
make npm-install-dev PKG=vitest  # Instala devDependency
```

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

## Estrutura do Projeto

```
CBN/
├── core/                  # Configurações Django (settings, urls, wsgi)
├── setup/                 # App Django: TODOS os models
│   ├── models.py          # Media, Status, Category, Tag, Role, Author, Post, etc.
│   ├── admin.py           # Registro de models no Django Admin
│   └── fixtures/          # Dados iniciais (initial_data.json)
├── homeNews/              # App Django: API pública (read-only)
├── painelControle/        # App Django: API admin (autenticada)
├── frontend/              # React + TypeScript + Vite + TailwindCSS
│   ├── src/
│   │   ├── components/    # Componentes reutilizáveis
│   │   ├── pages/         # Páginas (HomeNews, PainelControle)
│   │   ├── services/      # Axios + chamadas à API
│   │   ├── types/         # Interfaces TypeScript
│   │   └── routes/        # Definições de rotas
│   └── Dockerfile         # Container de desenvolvimento
├── docker/
│   └── postgres/
│       └── init_db.sh     # Cria banco do Keycloak automaticamente
├── docker-compose.yml     # Ambiente de desenvolvimento
├── docker-compose.prod.yml # Ambiente de produção (Traefik + Gunicorn)
├── Dockerfile             # Imagem da API Django
├── Makefile               # Comandos de desenvolvimento
├── .editorconfig          # Configuração de editores
└── .env.example           # Template de variáveis de ambiente
```

## API

A API segue o padrão REST com Django REST Framework.

**Endpoints Publicos** (`/api/`):
- `GET /api/posts/` — Lista de posts publicados (filtros: titulo, categoria, tag, autor)
- `GET /api/posts/{slug}/` — Detalhe de um post
- `GET /api/categories/` — Categorias
- `GET /api/tags/` — Tags
- `GET /api/home/` — Seções da home
- `GET /api/menus/` — Menus de navegação

**Documentação interativa:** Swagger UI em http://localhost:8000/api/schema/swagger/

## Dados Iniciais (Seed)

O comando `make seed` carrega dados iniciais para desenvolvimento:

- **Status:** DRAFT, PUBLISHED, ARCHIVED
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
