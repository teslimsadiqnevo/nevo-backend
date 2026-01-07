"""Database dependencies."""

from typing import AsyncGenerator

from src.infrastructure.database.session import AsyncSessionLocal
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.application.common.unit_of_work import IUnitOfWork


async def get_uow() -> AsyncGenerator[IUnitOfWork, None]:
    """Get Unit of Work dependency."""
    async with AsyncSessionLocal() as session:
        yield UnitOfWork(session)
