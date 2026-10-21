# Library Management System API

FastAPI library API for managing members and the books they borrow. Assignment 2
adds PostgreSQL persistence while retaining a selectable in-memory backend.

## Prerequisites

Install Python 3.11+ and PostgreSQL 14+. Create a database (for example,
`library`) and ensure the PostgreSQL server is running.

```sql
CREATE DATABASE library;
```

## Setup, configuration, and run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

The repository also includes `pyproject.toml` and `uv.lock` for reproducible
installs with uv:

```powershell
uv sync
Copy-Item .env.example .env
```

Edit `.env` with the PostgreSQL credentials for your machine:

```text
STORAGE_BACKEND=database
DATABASE_URL=postgresql+psycopg://postgres:change-me@localhost:5432/library
```

The database backend is the default and creates the tables at startup. To run
without PostgreSQL for temporary development, set `STORAGE_BACKEND=memory`.
Memory data is lost when the process stops.

```powershell
uvicorn app.main:app --reload --port 8000
```

Interactive documentation: [Swagger UI](http://localhost:8000/docs) and
[ReDoc](http://localhost:8000/redoc).

## Detailed setup documentation

- [Windows setup](docs/windows-setup.md)
- [Database and configuration](docs/database-and-configuration.md)

## API

`POST/GET /api/members`, `GET/PATCH/DELETE /api/members/{member_id}`,
`GET /api/members/{member_id}/books`, and
`POST/GET /api/books`, `GET/PATCH/DELETE /api/books/{book_id}` are available.
Creates return `201`, deletes return `204`, missing resources return `404`,
and duplicate values or deleting a member with books return `409`.

Example related requests:

```json
POST /api/members
{"name":"Alex Morgan","email":"alex.morgan@example.com","membership_id":"MEM-1001","phone":"+15551234567"}
```

```json
POST /api/books
{"title":"The Left Hand of Darkness","author":"Ursula K. Le Guin","isbn":"9780441478125","published_year":1969,"member_id":1}
```

## Project structure

```text
app/
├── config.py                 # typed settings and backend enum
├── database/
│   ├── __init__.py           # database infrastructure exports
│   └── session.py            # engine/session factory construction
├── dependencies.py           # FastAPI service dependencies
├── exceptions.py             # application outcomes
├── main.py                   # startup service selection and app
├── models/
│   ├── __init__.py            # imports/registers ORM models
│   ├── base.py               # SQLAlchemy declarative base
│   ├── member.py             # member table and relationship
│   └── book.py               # book table and relationship
├── repositories/
│   ├── members.py            # member queries and writes
│   └── books.py              # book queries and writes
├── schemas/
│   ├── __init__.py            # schema exports
│   ├── members.py             # member request/response schemas
│   └── books.py               # book request/response schemas
├── routers/
│   ├── http_errors.py        # application exception mapping
│   └── ...                   # HTTP endpoints
└── services/
    ├── in_memory_store.py    # process-local state
    ├── members/               # member service contract/backends
    └── books/                 # book service contract/backends
docs/
├── windows-setup.md           # Windows, Python, uv, and PostgreSQL setup
└── database-and-configuration.md
.env.example
pyproject.toml
requirements.txt
uv.lock
```
