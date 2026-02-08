# Usa uma imagem leve do Node 20
FROM node:20-alpine

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de dependência primeiro (para cachear a instalação)
COPY package*.json ./

# Instala as dependências
RUN npm install

# Copia o restante do código
COPY . .

RUN chown -R node:node /app

# Executa como usuário não-root
USER node

# Expõe a porta padrão do Vite
EXPOSE 5173

# Comando para rodar em modo desenvolvimento (com host liberado para o Docker)
CMD ["npm", "run", "dev", "--", "--host"]
