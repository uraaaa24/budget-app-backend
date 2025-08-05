# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


- Please answer in Japanese.
- Emojis are not allowed.
- If you have any doubts about a user's instructions or questions, stop working and ask.
- Implement test-driven development as mandatory, based on code excellence principles.
- Follow all t_wada's recommended way of proceeding when implementing TDD and Test Driven Development.
- Follow Martin Flower's recommendations for refactoring
- The design of this project follows the onion architecture approach

## Project Overview

Budget application backend built with FastAPI and PostgreSQL. Uses modern Python tooling with uv for package management and includes a full devcontainer setup.

## Development Environment

**Recommended Setup:** Use the VS Code devcontainer which provides:
- PostgreSQL 16 database
- All dependencies pre-installed
- Auto-start development server on port 8000

**Manual Setup:**
```bash
uv sync  # Install dependencies
```

## Common Commands

**Development Server:**
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Database:**
```bash
uv run python -m app.infrastructure.db.migrate  # Run migrations
```

**Code Quality:**
```bash
uv run mypy .        # Type checking (strict mode enabled)
uv run ruff check .  # Linting
uv run ruff format . # Code formatting
```

**Testing:**
```bash
uv run pytest              # Run all tests
uv run pytest -k test_name # Run specific test
```

## Architecture

**Planned Structure:** Modular FastAPI application with domain-driven design
- `app/main.py` - FastAPI application entry point
- `app/infrastructure/` - Database and external service integrations
- Domain layers for business logic (to be developed)

**Database:** PostgreSQL with psycopg driver
- Connection via `DB_DSN` environment variable
- Default: `postgresql+psycopg://budget:budget@db:5432/budget_app`

**Dependencies:**
- FastAPI for REST API
- Pydantic for data validation and serialization
- PostgreSQL for data persistence
- Python-dotenv for environment configuration

## Configuration

**Environment Variables:**
- `DB_DSN` - Database connection string
- `APP_ENV` - Application environment (dev/prod)
- Use `.env` files for local development

**Type Checking:** MyPy configured with strict mode
**Linting:** Ruff for both linting and formatting
