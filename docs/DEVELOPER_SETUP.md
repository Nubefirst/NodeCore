# NodeCore — настройка проекта для разработчика

Этот файл описывает запуск NodeCore на macOS, Linux или Windows. Основной сценарий запускает backend и PostgreSQL в Docker; локальный запуск backend через `uv` описан отдельно ниже.

## Требования

Для основного сценария понадобятся:

- Docker и Docker Compose
- Git

Для локальной разработки backend дополнительно установите Python 3.12+ и `uv`.

Проверить установки можно так:

```bash
docker --version
docker compose version
```

Для локальной разработки:

```bash
python --version
uv --version
```

## 1. Клонируйте проект

```bash
git clone <repo-url>
cd NodeCore
```

Далее все команды запускайте из корня проекта — там находятся `Dockerfile`, `compose.yaml` и `.env`.

## 2. Настройте переменные окружения

Скопируйте пример файла окружения:

```bash
cp .env.example .env
```

В Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Сгенерируйте уникальный секрет:

```bash
docker run --rm python:3.13-slim python -c "import secrets; print(secrets.token_hex(32))"
```

Замените `REPLACE_WITH_GENERATED_VALUE` в `.env` результатом команды. Не используйте один и тот же секрет в разных окружениях и не добавляйте `.env` в Git.

Замените пароль PostgreSQL `change_me` на свой и укажите его в `POSTGRES_PASSWORD`. В `DATABASE_URL` должны совпадать имя базы данных, пользователь и пароль.

Compose загружает параметры из корневого `.env`. Для backend-контейнера Compose задаёт адрес базы с хостом `postgres` — именем сервиса PostgreSQL внутри Compose-сети. Для описанного ниже локального запуска backend используйте `localhost` в `DATABASE_URL`.

## 3. Запустите проект в Docker

Текущий Compose-файл запускает backend и PostgreSQL; frontend из папки `frontend/` в Compose пока не настроен и автоматически не запускается.

Соберите image `nodecore-backend:latest` и запустите backend вместе с PostgreSQL:

```bash
docker compose up --build -d
```

Compose дождётся готовности PostgreSQL, применит миграции и запустит backend. Проверить состояние сервисов:

```bash
docker compose ps
```

Посмотреть логи backend:

```bash
docker compose logs -f backend
```

Приложение будет доступно по адресам:

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Остановить контейнеры, сохранив данные PostgreSQL:

```bash
docker compose down
```

## Локальная разработка backend (необязательно)

В этом режиме PostgreSQL работает в Docker, а backend запускается локально с автоматической перезагрузкой.

Установите зависимости из корня проекта:

```bash
uv sync
```

Убедитесь, что `DATABASE_URL` в `.env` использует `localhost` и те же имя базы, пользователя и пароль, что заданы переменными `POSTGRES_DB`, `POSTGRES_USER` и `POSTGRES_PASSWORD`.

Запустите PostgreSQL:

```bash
docker compose up -d postgres
```

Примените миграции и запустите backend:

```bash
uv run alembic upgrade head
uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## Полезные команды

### Пересобрать и запустить приложение в Docker

```bash
docker compose up --build -d
```

### Создать миграцию (локально)

```bash
uv run alembic revision --autogenerate -m "your migration name"
```

### Применить миграции (локально)

```bash
uv run alembic upgrade head
```

### Откатить миграцию (локально)

```bash
uv run alembic downgrade -1
```

### Проверить настройки приложения (локально)

```bash
uv run python -c "from backend.app.core.config import settings; print(settings.app_name, settings.database_url)"
```

## Структура проекта

```text
NodeCore/
├── backend/
│   └── app/
│       ├── api/
│       ├── core/
│       ├── db/
│       ├── models/
│       ├── repositories/
│       ├── schemas/
│       ├── security/
│       ├── services/
│       └── utils/
├── migrations/
├── frontend/
├── docs/
├── Dockerfile
├── compose.yaml
├── .env.example
├── .env
├── alembic.ini
├── pyproject.toml
├── README.md
├── ROADMAP.md
├── VISION.md
├── ARCHITECTURE.md
└── LICENSE
```

## Частые проблемы и решения

### Docker Compose не находит `.env`

Убедитесь, что команда запущена из корня проекта и файл `.env` создан из `.env.example`.

### PostgreSQL не запускается

Проверьте, что Docker запущен, и что порт из `POSTGRES_PORT` не занят:

```bash
docker compose ps
docker ps
```

### Ошибки подключения к базе данных

При запуске всего приложения в Docker backend должен подключаться к хосту `postgres`; Compose настраивает это автоматически. При локальном запуске backend адрес должен быть `localhost`. В обоих случаях проверьте соответствие `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` и `DATABASE_URL`.

### Ошибки импорта или модуль не найден при локальном запуске

Убедитесь, что вы запускаете команды из корня проекта и выполнили `uv sync`.

## Рекомендуемый ежедневный цикл разработки

Полностью в Docker:

```bash
docker compose up --build -d
docker compose logs -f backend
```

Локальный backend с PostgreSQL в Docker:

```bash
uv sync
docker compose up -d postgres
uv run alembic upgrade head
uv run uvicorn backend.app.main:app --reload
```

## Лицензия

Проект распространяется по лицензии MIT.
