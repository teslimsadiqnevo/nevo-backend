"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.app.main import create_app
from src.infrastructure.database.session import Base
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.core.config.constants import UserRole
from src.core.security import hash_password
from src.domain.entities.user import User
from src.domain.entities.school import School


# Test database URL (use SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def uow(db_session: AsyncSession) -> UnitOfWork:
    """Create Unit of Work for tests."""
    return UnitOfWork(db_session)


@pytest.fixture
def app():
    """Create test application."""
    return create_app()


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# Sample data fixtures
@pytest.fixture
def sample_school() -> School:
    """Create sample school."""
    return School(
        id=uuid4(),
        name="Test School",
        city="Lagos",
        country="Nigeria",
    )


@pytest.fixture
def sample_teacher(sample_school: School) -> User:
    """Create sample teacher."""
    return User(
        id=uuid4(),
        email="teacher@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.TEACHER,
        first_name="Test",
        last_name="Teacher",
        school_id=sample_school.id,
    )


@pytest.fixture
def sample_student(sample_school: School) -> User:
    """Create sample student."""
    return User(
        id=uuid4(),
        email="student@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.STUDENT,
        first_name="Test",
        last_name="Student",
        school_id=sample_school.id,
    )
