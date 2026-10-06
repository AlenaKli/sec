# File Manager

Учебный проект по безопасности. Веб-приложение для хранения файлов с аутентификацией и шифрованием.

## Стек технологий

- FastAPI
- JWT + bcrypt
- Fernet (шифрование файлов)
- Docker & Docker Compose

## Запуск

1. Клонировать репозиторий: `git clone ...`
2. Создать `.env`: `cp .env.example .env`
3. Установить зависимости: `pip install -r requirements.txt`
4. Запустить: `uvicorn src.main:app --reload`

## Вариант с Docker

1. Создать `.env`: `cp .env.example .env`
2. Запустить: `docker-compose up --build`

## API

Swagger UI: http://localhost:8000/docs
