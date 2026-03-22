"""Database engine and session factory."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from sitesmyth.config import Config
from sitesmyth.db.models import Base

_session_factory: sessionmaker[Session] | None = None


def get_engine(database_url: str | None = None):
    """Create or return the SQLAlchemy engine."""
    url = database_url or Config.load().database_url
    return create_engine(
        url,
        connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
        echo=False,
    )


def get_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    """Return the session factory, creating it if needed."""
    global _session_factory
    if _session_factory is None:
        engine = get_engine(database_url)
        _session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return _session_factory


def get_session(database_url: str | None = None) -> Session:
    """Create a new database session."""
    return get_session_factory(database_url)()


def init_db(cfg: Config | None = None) -> None:
    """Initialize database tables. Called by Alembic for migrations; app uses create_all for dev."""
    from sitesmyth.config import Config
    cfg = cfg or Config.load()
    engine = get_engine(cfg.database_url)
    Base.metadata.create_all(engine)
