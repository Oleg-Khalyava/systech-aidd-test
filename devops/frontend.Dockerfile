# Простой Dockerfile для Next.js Frontend
FROM node:20-alpine

WORKDIR /app

# Устанавливаем pnpm глобально
RUN npm install -g pnpm

# Копируем файлы зависимостей
COPY package.json pnpm-lock.yaml* ./

# Устанавливаем зависимости
RUN pnpm install

# Копируем код приложения (node_modules исключен через .dockerignore)
COPY . ./

# Открываем порт для Next.js dev server
EXPOSE 3000

# Запускаем dev сервер
CMD ["pnpm", "dev"]



