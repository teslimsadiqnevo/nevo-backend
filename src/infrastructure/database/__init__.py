"""Database module - SQLAlchemy setup and models."""

# Lazy imports to avoid triggering engine creation during Alembic migrations
def __getattr__(name: str):
    """Lazy import of database components."""
    if name == "get_db_session":
        from src.infrastructure.database.session import get_db_session
        return get_db_session
    elif name == "AsyncSessionLocal":
        from src.infrastructure.database.session import AsyncSessionLocal
        return AsyncSessionLocal
    elif name == "engine":
        from src.infrastructure.database.session import engine
        return engine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["get_db_session", "AsyncSessionLocal", "engine"]
