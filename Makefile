# ============================================================
# CBN - Makefile para Desenvolvimento Local
# ============================================================
# Uso: make <comando>
# Ajuda: make help
# ============================================================

.PHONY: help up down build rebuild rebuild-front logs logs-api logs-front logs-db logs-kc \
        migrate makemigrations superuser shell dbshell seed \
        npm-install npm-install-dev lint collectstatic \
        status ps clean reset setup \
        api-bash front-bash docs check

.DEFAULT_GOAL := help

# ------------------------------------------------------------
# Ajuda
# ------------------------------------------------------------
help: ## Mostra esta ajuda
	@echo ""
	@echo "  CBN - Comandos disponíveis"
	@echo "  =========================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "  Primeiro uso? Rode: make setup"
	@echo ""

# ------------------------------------------------------------
# Setup inicial
# ------------------------------------------------------------
setup: ## Primeiro setup completo (build + migrate + seed)
	@echo ""
	@echo "  ╔═════════════════════════════════╗"
	@echo "  ║       CBN - Setup Inicial       ║"
	@echo "  ╚═════════════════════════════════╝"
	@echo ""
	@echo "  [1/5] Verificando arquivos .env..."
	@test -f .env || (cp .env.example .env && echo "        .env criado a partir do .env.example")
	@test -f .env && echo "        .env OK"
	@test -f frontend/.env || (printf "NEXT_PUBLIC_API_URL=http://localhost:8000\nINTERNAL_API_URL=http://api:8000\nAUTH_SECRET=cbn-dev-auth-secret-change-in-production\nAUTH_KEYCLOAK_ID=cbn-frontend\nAUTH_KEYCLOAK_SECRET=cbn-dev-secret-change-in-production\nAUTH_KEYCLOAK_ISSUER=http://localhost:8080/realms/cbn\nKEYCLOAK_INTERNAL_URL=http://keycloak:8080\nAUTH_TRUST_HOST=true\n" > frontend/.env && echo "        frontend/.env criado")
	@test -f frontend/.env && echo "        frontend/.env OK"
	@echo ""
	@echo "  [2/5] Buildando imagens Docker..."
	@docker compose build --quiet
	@echo "        Build completo"
	@echo ""
	@echo "  [3/5] Subindo containers..."
	@docker compose up -d
	@echo ""
	@echo "  [4/5] Aguardando banco e rodando migrations..."
	@sleep 5
	@docker compose exec api python manage.py migrate --no-input
	@echo ""
	@echo "  [5/5] Carregando dados iniciais..."
	@docker compose exec api python manage.py loaddata initial_data || echo "        (fixtures já carregadas ou não encontradas)"
	@echo ""
	@echo "  ╔════════════════════════════════════════════════════════╗"
	@echo "  ║                    Setup concluído!                    ║"
	@echo "  ╠════════════════════════════════════════════════════════╣"
	@echo "  ║  Frontend:  http://localhost:3000                      ║"
	@echo "  ║  API:       http://localhost:8000                      ║"
	@echo "  ║  Admin:     http://localhost:8000/admin                ║"
	@echo "  ║  Swagger:   http://localhost:8000/api/schema/swagger/  ║"
	@echo "  ║  Keycloak:  http://localhost:8080                      ║"
	@echo "  ╚════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "  Proximo passo: make superuser"
	@echo ""

# ------------------------------------------------------------
# Docker Compose - Ciclo de vida
# ------------------------------------------------------------
up: ## Sobe todos os containers em background
	docker compose up -d

down: ## Para todos os containers
	docker compose down

build: ## Builda as imagens (api + frontend)
	docker compose build

rebuild: ## Rebuilda do zero (sem cache) e sobe
	docker compose build --no-cache
	docker compose up -d

restart: ## Reinicia todos os containers
	docker compose restart

restart-api: ## Reinicia apenas a API
	docker compose restart api

restart-front: ## Reinicia apenas o frontend
	docker compose restart frontend

rebuild-front: ## Rebuilda o frontend do zero (resolve erros de node_modules)
	docker compose rm -sf frontend
	docker compose build --no-cache frontend
	docker compose up -d -V frontend

# ------------------------------------------------------------
# Logs
# ------------------------------------------------------------
logs: ## Mostra logs de todos os serviços (ao vivo)
	docker compose logs -f

logs-api: ## Mostra logs da API Django (ao vivo)
	docker compose logs -f api

logs-front: ## Mostra logs do frontend React (ao vivo)
	docker compose logs -f frontend

logs-db: ## Mostra logs do PostgreSQL (ao vivo)
	docker compose logs -f db

logs-kc: ## Mostra logs do Keycloak (ao vivo)
	docker compose logs -f keycloak

# ------------------------------------------------------------
# Django - Banco de dados
# ------------------------------------------------------------
migrate: ## Roda as migrations
	docker compose exec api python manage.py migrate

makemigrations: ## Cria novas migrations após alterar models
	docker compose exec api python manage.py makemigrations

makemigrations-dry: ## Mostra o que seria gerado sem criar arquivos
	docker compose exec api python manage.py makemigrations --dry-run

showmigrations: ## Lista todas as migrations e status
	docker compose exec api python manage.py showmigrations

seed: ## Carrega dados iniciais (Status, Categorias, Tags, Roles, Menu)
	docker compose exec api python manage.py loaddata initial_data

# ------------------------------------------------------------
# Django - Utilitários
# ------------------------------------------------------------
superuser: ## Cria um superusuário Django
	docker compose exec api python manage.py createsuperuser

shell: ## Abre o shell interativo do Django
	docker compose exec api python manage.py shell

collectstatic: ## Coleta arquivos estáticos
	docker compose exec api python manage.py collectstatic --noinput

docs: ## Abre a documentação Swagger da API no navegador
	@echo "Abrindo Swagger UI..."
	@open http://localhost:8000/api/schema/swagger/ 2>/dev/null || \
		xdg-open http://localhost:8000/api/schema/swagger/ 2>/dev/null || \
		echo "Acesse: http://localhost:8000/api/schema/swagger/"

# ------------------------------------------------------------
# Acesso direto aos containers
# ------------------------------------------------------------
api-bash: ## Abre um terminal bash dentro do container da API
	docker compose exec api bash

front-bash: ## Abre um terminal sh dentro do container do frontend
	docker compose exec frontend sh

dbshell: ## Abre o psql conectado ao banco
	docker compose exec db psql -U postgres -d cbn_db

# ------------------------------------------------------------
# Frontend
# ------------------------------------------------------------
npm-install: ## Instala pacote npm (uso: make npm-install PKG=pacote)
	@if [ -z "$(PKG)" ]; then \
		echo "Uso: make npm-install PKG=nome-do-pacote"; \
		exit 1; \
	fi
	docker compose down
	cd frontend && npm install $(PKG)
	docker compose up -d --build

npm-install-dev: ## Instala pacote npm como devDependency (uso: make npm-install-dev PKG=pacote)
	@if [ -z "$(PKG)" ]; then \
		echo "Uso: make npm-install-dev PKG=nome-do-pacote"; \
		exit 1; \
	fi
	docker compose down
	cd frontend && npm install -D $(PKG)
	docker compose up -d --build

lint: ## Roda o ESLint no frontend
	docker compose exec frontend npm run lint

# ------------------------------------------------------------
# Verificação rápida
# ------------------------------------------------------------
check: ## Verifica se todos os serviços estão saudáveis
	@echo ""
	@echo "  Verificando serviços..."
	@echo ""
	@printf "  %-14s" "PostgreSQL:" && (docker compose exec db pg_isready -U postgres > /dev/null 2>&1 && echo "OK" || echo "FALHOU")
	@printf "  %-14s" "Django API:" && (curl -s -o /dev/null -w "" http://localhost:8000/api/ 2>/dev/null && echo "OK" || echo "FALHOU")
	@printf "  %-14s" "Frontend:" && (curl -s -o /dev/null -w "" http://localhost:3000/ 2>/dev/null && echo "OK" || echo "FALHOU")
	@printf "  %-14s" "Keycloak:" && (curl -s -o /dev/null -w "" http://localhost:8080/ 2>/dev/null && echo "OK" || echo "FALHOU")
	@echo ""

# ------------------------------------------------------------
# Status e limpeza
# ------------------------------------------------------------
status: ## Mostra o status dos containers e URLs
	@docker compose ps
	@echo ""
	@echo "  URLs:"
	@echo "  ─────────────────────────────────────────────────"
	@echo "  Frontend:  http://localhost:3000"
	@echo "  API:       http://localhost:8000/api/"
	@echo "  Admin:     http://localhost:8000/admin/"
	@echo "  Swagger:   http://localhost:8000/api/schema/swagger/"
	@echo "  ReDoc:     http://localhost:8000/api/schema/redoc/"
	@echo "  Keycloak:  http://localhost:8080"
	@echo ""

ps: ## Lista containers rodando (compacto)
	docker compose ps

clean: ## Para containers e remove volumes (APAGA dados do banco!)
	@echo "  ATENCAO: Isso vai APAGAR todos os dados do banco local!"
	@read -p "  Tem certeza? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	docker compose down -v
	rm -rf local_pg_data

reset: ## Reset completo: limpa tudo e rebuilda do zero
	@echo "  ATENCAO: Isso vai APAGAR tudo e reconstruir do zero!"
	@read -p "  Tem certeza? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	docker compose down -v
	rm -rf local_pg_data
	docker compose build --no-cache
	docker compose up -d
	@echo "  Aguardando banco..."
	@sleep 5
	docker compose exec api python manage.py migrate --no-input
	docker compose exec api python manage.py loaddata initial_data || true
	@echo ""
	@echo "  Reset completo. Rode 'make superuser' para criar o admin."
