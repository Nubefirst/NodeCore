# NodeCore — настройка проекта для разработчика

Этот файл описывает, как быстро подготовить проект к локальной разработке на macOS, Linux или Windows.

## Требования

Перед началом убедитесь, что у вас установлены:

- Python 3.12+
- uv
- Docker и Docker Compose
- Git

Проверить установку можно так:

```bash
python --version
uv --version
docker --version
docker compose version
```

## 1. Клонируйте проект

```bash
git clone <repo-url>
cd NodeCore
```

## 2. Установите зависимости через uv

В корне проекта выполните:

```bash
uv sync
```

После этого будет создано виртуальное окружение `.venv` и установятся зависимости из `pyproject.toml`.

### Активация виртуального окружения

#### macOS / Linux

```bash
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

#### Windows CMD

```cmd
.venv\Scripts\activate.bat
```

## 3. Настройте переменные окружения

Скопируйте пример файла окружения:

```bash
cp .env.example .env
```

Если вы на Windows PowerShell, используйте:

```powershell
Copy-Item .env.example .env
```

Проверьте содержимое `.env`:

```bash
cat .env
```

Обычно там должно быть что-то вроде:

```env
APP_NAME=NodeCore
APP_VERSION=0.1.0
DEBUG=true

POSTGRES_DB=nodecore
POSTGRES_USER=nodecore
POSTGRES_PASSWORD=change_me
POSTGRES_PORT=5432

DATABASE_URL=postgresql+psycopg://nodecore:nodecore_password@localhost:5432/nodecore
```

> Для локального запуска можно оставить значения по умолчанию, но лучше заменить пароль на свой.

## 4. Поднимите PostgreSQL через Docker

```bash
docker compose up -d postgres
```

Проверить статус контейнера:

```bash
docker compose ps
```

## 5. Примените миграции базы данных

```bash
uv run alembic upgrade head
```

## 6. Запустите backend

```bash
uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

После этого приложение будет доступно по адресам:

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Полезные команды

### Запуск приложения

```bash
uv run uvicorn backend.app.main:app --reload
```

### Создание миграции

```bash
uv run alembic revision --autogenerate -m "your migration name"
```

### Применение миграций

```bash
uv run alembic upgrade head
```

### Откат миграции

```bash
uv run alembic downgrade -1
```

### Проверка настроек приложения

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
├── .env.example
├── .env
├── alembic.ini
├── compose.yaml
├── pyproject.toml
├── README.md
├── ROADMAP.md
├── VISION.md
├── ARCHITECTURE.md
└── LICENSE
```

## Частые проблемы и решения

### PostgreSQL не запускается

Проверьте, что Docker запущен, и что порт в `.env` не занят:

```bash
docker ps
```

### Ошибки импорта или модуль не найден

Убедитесь, что вы запускаете команды из корня проекта:

```bash
pwd
ls
```

И что зависимости установлены через `uv sync`.

### Проблемы с Alembic

Проверьте, что `DATABASE_URL` в `.env` совпадает с настройками PostgreSQL:

```bash
cat .env
```

## Рекомендуемый ежедневный цикл разработки

```bash
uv sync
docker compose up -d postgres
uv run alembic upgrade head
uv run uvicorn backend.app.main:app --reload
```

## Лицензия

Проект распространяется по лицензии MIT.
