# Library Management System API

Assignment 1 implementation using Python and FastAPI. The API manages Members and the Books they have borrowed using in-memory storage.

Data is intentionally lost when the application restarts. Database persistence is reserved for Assignment 2.

## Setup and Run

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the development server:

```powershell
uvicorn app.main:app --reload --port 8000
```

Interactive API documentation is available at:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/members` | Create a member |
| `GET` | `/api/members` | List members |
| `GET` | `/api/members/{member_id}` | Get one member |
| `PATCH` | `/api/members/{member_id}` | Update a member |
| `DELETE` | `/api/members/{member_id}` | Delete a member without books |
| `GET` | `/api/members/{member_id}/books` | List a member's books |
| `POST` | `/api/books` | Create a book |
| `GET` | `/api/books` | List books |
| `GET` | `/api/books/{book_id}` | Get one book |
| `PATCH` | `/api/books/{book_id}` | Update a book |
| `DELETE` | `/api/books/{book_id}` | Delete a book |

Successful creates return `201 Created`. Successful deletes return `204 No Content`. Missing resources return `404 Not Found`, and duplicate values or attempts to delete a member with books return `409 Conflict`.

## Example Requests

Create a member:

```json
POST /api/members
{
	"name": "Alex Morgan",
	"email": "alex.morgan@example.com",
	"membership_id": "MEM-1001",
	"phone": "+15551234567"
}
```

Create a book associated with member `1`:

```json
POST /api/books
{
	"title": "The Left Hand of Darkness",
	"author": "Ursula K. Le Guin",
	"isbn": "9780441478125",
	"published_year": 1969,
	"member_id": 1
}
```

Retrieve that member's books:

```text
GET /api/members/1/books
```

## Validation Rules

- Book titles are 1-200 characters after trimming whitespace.
- Book authors are 1-120 characters after trimming whitespace.
- ISBN values are required and unique.
- Publication years must be between 1450 and the current year.
- `member_id` must identify an existing member.
- Member names are 1-120 characters after trimming whitespace.
- Member emails must be valid and unique.
- Membership IDs must be unique.
- Phone numbers use an optional leading `+` followed by 8-15 digits.

## Project Structure

```text
app/
├── main.py
├── models/
│   └── schemas.py
├── routers/
│   ├── books.py
│   └── members.py
└── services/
		└── storage.py
requirements.txt
```