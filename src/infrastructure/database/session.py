"""Database session configuration."""

from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.core.config.settings import settings

# Base class for models (defined first, before engine)
# This allows models to import Base without triggering engine creation
Base = declarative_base()

# Lazy engine creation to defer initialization until first use
_engine: Optional[AsyncEngine] = None
_AsyncSessionLocal: Optional[async_sessionmaker] = None


def _get_engine() -> AsyncEngine:
    """Get or create async engine (lazy initialization)."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.database_echo,
            future=True,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
    return _engine


def _get_session_factory() -> async_sessionmaker:
    """Get or create async session factory (lazy initialization)."""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            _get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _AsyncSessionLocal


# Lazy properties - only create engine when accessed
class _LazyEngine:
    """Lazy engine wrapper."""
    def __getattr__(self, name: str):
        return getattr(_get_engine(), name)


class _LazySessionFactory:
    """Lazy session factory wrapper."""
    def __call__(self, *args, **kwargs):
        return _get_session_factory()(*args, **kwargs)
    
    def __getattr__(self, name: str):
        return getattr(_get_session_factory(), name)


# Export lazy versions
engine = _LazyEngine()
AsyncSessionLocal = _LazySessionFactory()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    session_factory = _get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
