# 🔐 Configuração do Keycloak (Autenticação)

Este projeto agora utiliza Keycloak para autenticação. Siga os passos abaixo ao rodar o projeto pela primeira vez.

## 1. Subindo o Ambiente
```bash
docker compose up -d --build
```

## 2. Configuração Inicial do Banco (Primeira vez apenas)
Se o container do Keycloak ficar reiniciando com erro `database not found`:
```bash
# Crie o banco manualmente
docker compose exec db psql -U postgres -c "CREATE DATABASE keycloak;"
docker compose restart keycloak
```

## 3. Configurando o Painel (Manual)
Acesse http://localhost:8080 (Login: admin / Senha: ver .env)

1. **Criar Realm:**
   - Clique em "Master" (topo esquerdo) -> "Create Realm".
   - Nome: `exemplo`.

2. **Criar Client (Conexão Frontend):**
   - Menu "Clients" -> "Create client".
   - Client ID: `exemplo-frontend`.
   - Login Settings:
     - Valid Redirect URIs: `http://localhost:5173/*`
     - Web Origins: `+`

3. **Criar Usuário:**
   - Menu "Users" -> "Add user".
   - Username: `seu-user`.
   - Aba "Credentials" -> "Set password" -> Defina a senha (desmarque "Temporary").

## 4. Vínculo com Django (Importante!)
Para que o autor consiga criar posts, ele precisa existir no Django:

1. Acesse http://localhost:8000/admin (Superusuário).
2. Crie um Usuário com **o mesmo username** do Keycloak (ex: `seu-user`).
3. Vá em "Autores" e crie um Autor, vinculando-o a esse Usuário.