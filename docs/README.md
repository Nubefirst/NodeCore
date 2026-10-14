# NodeCore

> Modern platform for Linux server management and infrastructure administration.

NodeCore — это долгосрочный учебный инженерный проект, цель которого — создать современную платформу управления Linux-серверами, одновременно изучая backend-разработку, архитектуру, DevOps и информационную безопасность.

Проект развивается постепенно. Каждая новая функция появляется как ответ на реальную инженерную задачу, а не ради использования новой технологии.

---

## Goals

Основные цели проекта:

- изучение современной backend-разработки;
- проектирование масштабируемой архитектуры;
- работа с Linux и Docker;
- изучение сетей и безопасности;
- получение опыта командной разработки;
- создание качественного проекта для портфолио.

---

## Current Status

🚧 Проект находится на ранней стадии разработки.

Текущая версия:

```
Version 0.1 — Foundation
```

---

## Planned Features

На текущий момент планируется реализация следующих возможностей:

- Authentication & Authorization
- User Management
- Server Monitoring
- Docker Management
- Audit Logging
- Notifications
- Infrastructure Management

Полный список доступен в [ROADMAP.md](ROADMAP.md).

---

## Repository Structure

```
NodeCore/
├── backend/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEVELOPER_SETUP.md
│   ├── README.md
│   ├── ROADMAP.md
│   └── VISION.md
├── migrations/
├── scripts/
├── tests/
├── pyproject.toml
└── uv.lock
```

---

## Documentation

- [VISION.md](VISION.md) — долгосрочное видение проекта.
- [ROADMAP.md](ROADMAP.md) — план развития.
- [ARCHITECTURE.md](ARCHITECTURE.md) — архитектурные решения.
- [DEVELOPER_SETUP.md](DEVELOPER_SETUP.md) — настройка окружения разработчика.
- `CONTRIBUTING.md` *(будет добавлен позже)*.

---

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Docker

### Frontend

- React
- TypeScript

---

## Development Workflow

Проект разрабатывается с использованием:

- Git Flow
- Feature Branches
- Pull Requests
- Code Review
- Documentation First

---

## Philosophy

NodeCore не стремится использовать как можно больше технологий.

Каждая новая технология появляется только тогда, когда проект действительно начинает в ней нуждаться.

Мы рассматриваем проект как инженерную площадку, а не как набор CRUD-страниц.

---

## License

This project is licensed under the MIT License.