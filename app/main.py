from fastapi import FastAPI

from app.routers import books, members

app = FastAPI(
    title="Library Management System API",
    version="1.0.0",
    description="An in-memory API for managing library members and borrowed books.",
)

app.include_router(books.router)
app.include_router(members.router)


@app.get("/", tags=["health"], summary="Check API health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
