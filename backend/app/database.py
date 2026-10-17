"""SQLAlchemy Database configuration and session management."""

import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from app.config import get_settings

logger = logging.getLogger("biztwin.database")

settings = get_settings()

# Configure SQLite-specific parameters safely
is_sqlite = settings.database_url.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}
engine_kwargs = {"connect_args": connect_args, "echo": settings.debug}

# Use StaticPool for in-memory SQLite to share database state across threads/sessions
if settings.database_url in ("sqlite://", "sqlite:///:memory:"):
    from sqlalchemy.pool import StaticPool
    engine_kwargs["poolclass"] = StaticPool

# Engine configuration
engine = create_engine(
    settings.database_url,
    **engine_kwargs,
)

# Thread-safe session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Base declarative class for all BizTwin ORM models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a SQLAlchemy session.

    Guarantees session cleanup upon request completion.
    Transaction commits or rollbacks must be explicitly managed by callers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(bind_engine=None) -> None:
    """Safely initialize database tables if they do not exist."""
    # Ensure all models are discovered and registered with Base.metadata
    import app.models  # noqa: F401

    target = bind_engine or engine
    logger.info("Initializing database tables on engine: %s", target.url.render_as_string(hide_password=True))
    Base.metadata.create_all(bind=target)
