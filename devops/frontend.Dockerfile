# Простой Dockerfile для Next.js Frontend
FROM node:20-alpine

WORKDIR /app

# Устанавливаем pnpm глобально
RUN npm install -g pnpm

# Копируем файлы зависимостей из папки frontend
COPY frontend/package.json frontend/pnpm-lock.yaml* ./

# Устанавливаем зависимости
RUN pnpm install

# Копируем код приложения из папки frontend (node_modules исключен через .dockerignore)
COPY frontend/ ./

# Открываем порт для Next.js dev server
EXPOSE 3000

# Запускаем dev сервер
CMD ["pnpm", "dev"]



