# Imagem base com Node.js e TypeScript
FROM node:18

# Diretório de trabalho
WORKDIR /app

# Copia os arquivos de configuração
COPY package*.json ./
COPY tsconfig.json ./

# Instala as dependências
RUN npm install

# Copia o código fonte
COPY src ./src

# Compila o TypeScript
RUN npm run build

# Expõe a porta
EXPOSE 3002

# Comando para iniciar o serviço
CMD ["npm", "start"]
