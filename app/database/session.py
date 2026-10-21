from dataclasses import dataclass

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings


@dataclass(frozen=True)
class DatabaseInfrastructure:
    engine: Engine
    session_factory: sessionmaker[Session]


def create_database(settings: Settings) -> DatabaseInfrastructure:
    engine = create_engine(
        settings.database_url,
        echo=settings.database_echo_sql,
        pool_pre_ping=True,
    )
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return DatabaseInfrastructure(engine=engine, session_factory=factory)
