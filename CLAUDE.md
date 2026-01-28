# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

InConnect (迎客通) is a hotel customer experience platform with intelligent message routing and ticket management. It's a monorepo containing:
- **Backend**: FastAPI (Python 3.11+) with async SQLAlchemy, PostgreSQL, Redis, RabbitMQ
- **Frontend**: React 18 + TypeScript + Vite + Ant Design

## Development Commands

### Backend (from `/backend`)
```bash
uv sync                                           # Install dependencies
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000  # Dev server
uv run pytest tests/ -v                           # Run all tests
uv run pytest tests/test_api.py -v                # Run specific test file
uv run pytest tests/ -k "test_create_ticket"      # Run tests matching pattern
uv run pytest tests/ --cov=app                    # Run with coverage
uv run ruff check backend/ && uv run ruff format backend/  # Lint & format
uv run mypy backend/                              # Type checking
uv run alembic upgrade head                       # Run migrations
uv run alembic revision --autogenerate -m "msg"   # Create migration
```

### Frontend (from `/frontend`)
```bash
npm install         # Install dependencies
npm run dev         # Dev server (port 3000)
npm run build       # Production build (runs tsc first)
npm run lint        # ESLint check
```

### Docker
```bash
docker-compose up                              # Development environment
docker-compose -f docker-compose.prod.yml up   # Production environment
```

## Architecture

### Backend Layered Structure (`backend/app/`)
```
api/v1/       → FastAPI routers (HTTP request handling)
services/     → Business logic & orchestration
crud/         → Database operations (extends CRUDBase generic class)
models/       → SQLAlchemy ORM definitions
schemas/      → Pydantic request/response validation
core/         → Cross-cutting: auth, exceptions, security, logging, permissions
```

### Key Patterns

**Dependency Injection**: FastAPI `Depends()` for db sessions (`get_db`), auth (`get_current_user_id`)

**Generic CRUD Base**: `CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]` provides get, get_multi, create, update, delete

**Unified API Response**: All endpoints return `{code, message, data}` via `APIResponse` schema

**Business Exceptions**: `BusinessException(code, message)` with subclasses (ValidationError, NotFoundError, PermissionDeniedError) - global handler converts to APIResponse

**Error Codes**: TICKET_NOT_FOUND=2001, MESSAGE_SEND_FAILED=3001, etc. (see `core/exceptions.py`)

**Async Everything**: SQLAlchemy AsyncSession, async service methods, asyncio-compatible tests

### Frontend State Management (`frontend/src/stores/`)
Zustand stores with localStorage persistence for: auth, ticket, report, template

### Data Model Relationships
```
Hotel 1:N → Staff, Conversation, Ticket
Conversation 1:N → Message
Ticket N:1 → Staff (assigned_to), 1:N → TicketTimeline
RoutingRule N:1 → Hotel
```

### Ticket Enums (backend/app/models/ticket.py)
- Status: PENDING, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED, REOPENED
- Priority: P1, P2, P3, P4
- Category: MAINTENANCE, HOUSEKEEPING, SERVICE, COMPLAINT, INQUIRY, OTHER

## Services & Ports

| Service | Port | Description |
|---------|------|-------------|
| FastAPI | 8000 | Backend API |
| React | 3000 | Admin frontend |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache |
| RabbitMQ | 15672 | Queue management UI |
| Elasticsearch | 9200 | Search |
| MinIO | 9001 | Object storage UI |

## Testing

Test markers: `@pytest.mark.slow`, `@pytest.mark.integration`, `@pytest.mark.unit`

Tests use `pytest-asyncio` for async support. Fixtures in `tests/conftest.py`.

## Code Style

- **Python**: ruff (100 char lines), mypy strict mode with Pydantic plugin
- **TypeScript**: ESLint with react-hooks and react-refresh plugins
- **Pre-commit**: Configured with ruff, mypy, bandit security checks

## Ralph Loop

This project uses the Ralph Wiggum Loop development methodology. Configuration in `.ralph/` includes task.md, context.md, constraints.md for iterative context-window development with memory persisted via git and text files.
