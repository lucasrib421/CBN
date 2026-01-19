# 📰 Backend - Portal de Notícias

Este repositório contém o código fonte do Backend (API) do nosso portal jornalístico. O projeto foi construído focando em escalabilidade e facilidade de desenvolvimento utilizando containers.

## 🛠 Tecnologias Principais

* **Linguagem:** Python 3.12+
* **Framework Web:** Django 6.0
* **API:** Django Rest Framework (DRF)
* **Banco de Dados:** PostgreSQL 15
* **Infraestrutura:** Docker & Docker Compose
* **Servidor de Aplicação:** Gunicorn (Produção)
* **Proxy Reverso:** Traefik (Produção)

---

## 🚀 Como rodar o projeto localmente

Graças ao Docker, você não precisa instalar Python ou PostgreSQL na sua máquina. Siga os passos abaixo:

### 1. Pré-requisitos
Certifique-se de ter instalado:
* [Git](https://git-scm.com/)
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Inicie ele antes de começar)

### 2. Clonar o repositório
```bash
git clone [https://github.com/lucasrib421/CBN](https://github.com/lucasrib421/CBN)
cd SEU-REPOSITORIO
```

### 3. Configurar Variáveis de Ambiente
Crie um arquivo chamado .env na raiz do projeto. Copie e cole o conteúdo abaixo (configuração padrão para desenvolvimento):

```
# Configurações do Django
DEBUG=True
SECRET_KEY=chave-secreta-para-desenvolvimento-local
ALLOWED_HOSTS=localhost,127.0.0.1

# Configurações do Banco de Dados (Docker)
POSTGRES_DB=news_local_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### 4. Subir os Containers
Execute o comando abaixo para construir e iniciar o ambiente:

```
docker compose up -d
```
Isso vai baixar as imagens, instalar as dependências e subir o banco de dados e a API.

### 5. Configurar o Banco de Dados
Na primeira vez, você precisa criar as tabelas e um usuário administrador:

```
# Criar as tabelas no banco
docker compose exec api python manage.py migrate

# Criar um superusuário (Siga as instruções na tela)
docker compose exec api python manage.py createsuperuser
```

### 🔗 Acessando o Projeto
Após rodar os comandos acima, o sistema estará disponível em:

Painel Admin: http://127.0.0.1:8000/admin

API Root: http://127.0.0.1:8000/

## ⚠️ Nota Importante sobre o Banco de Dados
Para evitar conflitos com bancos de dados já instalados na sua máquina (como um Postgres local rodando na porta 5432), o container do banco expõe a porta 5433 para o host.

Se você quiser conectar uma ferramenta externa (DBeaver, PGAdmin, SQLTools) ao banco do Docker, use:

Host: localhost

Port: 5433 (Não use 5432)

User/Pass: postgres / postgres

Database: news_local_db


## 📦 Comandos Úteis no Dia a Dia
Sempre que precisar rodar comandos do Django (manage.py), use o prefixo docker compose exec api:   

Criar novas migrações (após editar models):
```
docker compose exec api python manage.py makemigrations
```

Aplicar migrações:
```
docker compose exec api python manage.py migrate
```

Derrubar o ambiente:
```
docker compose down
```

Ver logs de erro:
```
docker compose logs -f api
```

## ☁️ Deploy (Produção)
Para o ambiente de produção, utilizamos o arquivo docker-compose.prod.yml, que configura o Traefik (SSL automático) e o Gunicorn. Não use este arquivo localmente.