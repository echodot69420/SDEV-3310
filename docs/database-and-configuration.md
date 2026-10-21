# Database and configuration

Assignment 2 uses PostgreSQL as the default backend and retains an in-memory
backend for temporary development. The application selects the backend once at
startup from the typed settings in `app/config.py`.

## Backend selection

Create `.env` from `.env.example`:

```powershell
Copy-Item .env.example .env
```

For PostgreSQL persistence:

```text
STORAGE_BACKEND=database
DATABASE_URL=postgresql+psycopg://postgres:your-password@localhost:5432/library
DATABASE_ECHO_SQL=false
```

For process-local memory:

```text
STORAGE_BACKEND=memory
DATABASE_URL=postgresql+psycopg://postgres:change-me@localhost:5432/library
DATABASE_ECHO_SQL=false
```

The database URL must use the `postgresql+psycopg://` scheme. The URL is
validated when settings load, even when the memory backend is selected.

`.env` contains local credentials and must not be committed. The committed
`.env.example` file is only a template.

## PostgreSQL initialization

PostgreSQL must be running and the `library` database must exist before the
database backend starts:

```sql
CREATE DATABASE library;
```

The API creates missing tables with SQLAlchemy metadata at startup. It does not
run migrations and does not create the PostgreSQL database itself.

## Persistence layers

The application follows the same layered arrangement as the course
Project-and-Task example:

1. Routers validate HTTP input, call service contracts, and translate
   application exceptions into HTTP responses.
2. Services implement Library use cases and business rules.
3. Repositories perform SQLAlchemy queries and writes.
4. ORM models define database tables and relationships.
5. `app/database/session.py` creates one application-scoped Engine and session
   factory.

Each database service operation creates its own short-lived Session. Write
operations use `sessionmaker.begin()`, which commits on success and rolls back
when an exception escapes.

The Member-to-Book relationship is represented by the `books.member_id`
foreign key. Member deletion checks for related Books in the same transaction,
so a Member with Books returns a conflict and is not deleted.

## Verifying persistence

1. Start the API with `STORAGE_BACKEND=database`.
2. Create a Member and a related Book through Swagger UI.
3. Stop the API.
4. Start it again with the same `.env`.
5. Retrieve the Member and Book.

The records should still exist after the restart. Set
`DATABASE_ECHO_SQL=true` temporarily when inspecting SQL statements during local
development, then turn it back off.
