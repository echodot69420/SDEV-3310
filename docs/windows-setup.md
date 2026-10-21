# Windows setup

Use **Windows Terminal with a PowerShell tab** for the commands in this guide.

## 1. Check the tools

Confirm that Git and Python are available:

```powershell
git --version
python --version
```

This project requires Python 3.11 or newer. If Git is not recognized, install
[Git for Windows](https://git-scm.com/install/windows), then close and reopen
Windows Terminal.

The project supports either a standard Python virtual environment or
[uv](https://docs.astral.sh/uv/). To install uv with PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close and reopen Windows Terminal, then verify it:

```powershell
uv --version
```

## 2. Open the project

If the repository is not cloned yet:

```powershell
cd $HOME
git clone https://github.com/echodot69420/SDEV-3310.git
cd SDEV-3310
git switch assignment-2
```

If the repository is already cloned, open PowerShell in the existing
`SDEV-3310` folder and switch to `assignment-2`.

## 3. Install Python dependencies

Using uv and the committed lockfile:

```powershell
uv sync
```

Or using the standard Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, either allow it for the current user or use
uv instead:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 4. Install and start PostgreSQL

1. Download the [PostgreSQL Windows installer](https://www.postgresql.org/download/windows/).
2. Keep the default port, `5432`.
3. Remember the password chosen for the `postgres` user.
4. Keep PostgreSQL Server and Command Line Tools selected. pgAdmin is optional.

Find the PostgreSQL Windows service:

```powershell
Get-Service *postgres*
```

If it is stopped, start it with the exact service name shown by that command:

```powershell
Start-Service -Name "postgresql-x64-18"
```

## 5. Create the library database

The API creates its tables at startup, but the PostgreSQL database itself must
exist first. Replace the executable path if PostgreSQL was installed elsewhere:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d postgres
```

At the `postgres=#` prompt, run:

```sql
CREATE DATABASE library;
\q
```

If the database already exists, PostgreSQL reports that fact and no data is
changed.

You can verify the database:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d library -c "\dt"
```

The table list may be empty before the API first starts.

## 6. Configure the application

Create a local environment file from the safe template:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and replace `change-me` with the password for your local
PostgreSQL user:

```text
STORAGE_BACKEND=database
DATABASE_URL=postgresql+psycopg://postgres:change-me@localhost:5432/library
DATABASE_ECHO_SQL=false
```

Do not commit `.env`. It is ignored by Git. Keep `.env.example` safe and free
of real credentials.

For temporary development without PostgreSQL, use:

```text
STORAGE_BACKEND=memory
DATABASE_URL=postgresql+psycopg://postgres:change-me@localhost:5432/library
```

## 7. Start and verify the API

With uv:

```powershell
uv run uvicorn app.main:app --reload --port 8000
```

With an activated virtual environment:

```powershell
uvicorn app.main:app --reload --port 8000
```

Open these URLs:

- [Swagger UI](http://localhost:8000/docs)
- [ReDoc](http://localhost:8000/redoc)
- [Health check](http://localhost:8000/)

After the first database-backed startup, verify that the tables exist:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d library -c "\dt"
```

## 8. Optional PostgreSQL PATH setup

To use `psql` without its full path:

1. Open **Environment Variables** from the Windows Start menu.
2. Select **Edit the system environment variables**.
3. Click **Environment Variables**.
4. Edit the user `Path`.
5. Add:

```text
C:\Program Files\PostgreSQL\18\bin
```

6. Close and reopen Windows Terminal.
7. Verify:

```powershell
psql --version
```
