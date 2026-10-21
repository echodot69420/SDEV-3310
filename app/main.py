from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models
from app.config import Settings, StorageBackend
from app.database import create_database
from app.models.base import Base
from app.routers import books, members
from app.services.books import DatabaseBookService, InMemoryBookService
from app.services.in_memory_store import InMemoryStore
from app.services.members import DatabaseMemberService, InMemoryMemberService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    app.state.settings = settings
    if settings.storage_backend == StorageBackend.DATABASE:
        database = create_database(settings)
        app.state.database = database
        app.state.engine = database.engine
        app.state.session_factory = database.session_factory
        Base.metadata.create_all(bind=database.engine)
        app.state.member_service = DatabaseMemberService(database.session_factory)
        app.state.book_service = DatabaseBookService(database.session_factory)
    else:
        store = InMemoryStore()
        app.state.store = store
        app.state.member_service = InMemoryMemberService(store)
        app.state.book_service = InMemoryBookService(store)
    yield
    if hasattr(app.state, "engine"):
        app.state.engine.dispose()


app = FastAPI(
    title="Library Management System API",
    version="2.0.0",
    description="A layered API for managing library members and borrowed books.",
    openapi_tags=[
        {"name": "health", "description": "Service health checks."},
        {"name": "members", "description": "Library member management."},
        {"name": "books", "description": "Library book management."},
    ],
    lifespan=lifespan,
)
app.include_router(books.router)
app.include_router(members.router)


@app.get("/", tags=["health"], summary="Check API health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
