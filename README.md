# Task API

A multi-user task management REST API built with **FastAPI**, **PostgreSQL** and **SQLAlchemy**.
Users sign up, log in with JWT authentication, and manage their own tasks.

## Features
- Signup / login with bcrypt-hashed passwords and JWT access tokens
- Full CRUD for tasks, with pagination and `is_done` filtering
- Per-user data isolation: a user can never read or change another user's tasks
- Request validation with Pydantic; schema versioning with Alembic migrations
- Automated tests with pytest, run against a real PostgreSQL database
- Auto-generated interactive API docs (Swagger UI)

## Tech stack
Python 3.12+, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16 (Docker), pytest

## Project structure
```
app/
  main.py        # app creation and router wiring
  database.py    # settings, engine, session dependency
  models.py      # SQLAlchemy tables
  schemas.py     # Pydantic request/response models
  security.py    # password hashing, JWT, current-user dependency
  crud.py        # all database queries
  routers/       # auth and tasks endpoints
tests/           # pytest suite
alembic/         # database migrations
```

## Getting started

Prerequisites: Python 3.12+, Docker Desktop.

```bash
git clone <your-repo-url> && cd taskapi
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # then set a real SECRET_KEY
docker compose up -d          # start PostgreSQL
alembic upgrade head          # create the tables
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for the interactive API docs.

## Running the tests

```bash
docker compose exec db psql -U taskapi -d taskapi -c "CREATE DATABASE taskapi_test;"
pytest -v
pytest --cov=app --cov-report=term-missing
```

## API overview

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /auth/signup | no | Create an account |
| POST | /auth/login | no | Get a JWT access token |
| POST | /tasks | yes | Create a task |
| GET | /tasks | yes | List your tasks (`skip`, `limit`, `is_done`) |
| GET | /tasks/{id} | yes | Get one task |
| PATCH | /tasks/{id} | yes | Partially update a task |
| DELETE | /tasks/{id} | yes | Delete a task |

## Design decisions
- **Layered structure**: routers handle HTTP, `crud.py` handles data access, `security.py` handles auth.
- **Stateless JWT auth**: any app instance can serve any request, which makes horizontal scaling easy.
  Trade-off: tokens can't be revoked before expiry.
- **Authorization by query scoping**: every task query filters by `owner_id`. Another user's task returns 404, not 403, so its existence isn't revealed.
- **Migrations over `create_all()`**: schema changes are versioned and reversible.

## Known limitations / next steps
- Refresh tokens and token revocation
- Rate limiting on login
- Optimistic locking for concurrent updates
- CI pipeline (GitHub Actions) and cloud deployment
- Run Alembic migrations in the test setup