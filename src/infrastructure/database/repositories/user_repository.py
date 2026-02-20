"""User repository implementation."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.constants import UserRole
from src.domain.entities.user import User
from src.domain.interfaces.repositories import IUserRepository
from src.domain.value_objects.pagination import PaginatedResult, PaginationParams
from src.infrastructure.database.models.user import UserModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[UserModel, User], IUserRepository):
    """User repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserModel)

    def _to_entity(self, model: UserModel) -> User:
        """Convert model to entity."""
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            role=model.role,
            first_name=model.first_name,
            last_name=model.last_name,
            age=model.age,
            school_id=model.school_id,
            is_active=model.is_active,
            is_verified=model.is_verified,
            avatar_url=model.avatar_url,
            phone_number=model.phone_number,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login_at=model.last_login_at,
            linked_student_ids=model.linked_student_ids or [],
            nevo_id=model.nevo_id,
            pin_hash=model.pin_hash,
            class_code=model.class_code,
        )

    def _to_model(self, entity: User) -> UserModel:
        """Convert entity to model."""
        return UserModel(
            id=entity.id,
            email=entity.email,
            password_hash=entity.password_hash,
            role=entity.role,
            first_name=entity.first_name,
            last_name=entity.last_name,
            age=entity.age,
            school_id=entity.school_id,
            is_active=entity.is_active,
            is_verified=entity.is_verified,
            avatar_url=entity.avatar_url,
            phone_number=entity.phone_number,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            last_login_at=entity.last_login_at,
            linked_student_ids=entity.linked_student_ids,
            nevo_id=entity.nevo_id,
            pin_hash=entity.pin_hash,
            class_code=entity.class_code,
        )

    async def create(self, user: User) -> User:
        """Create a new user."""
        model = self._to_model(user)
        created = await self._create(model)
        return self._to_entity(created)

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        model = await self._get_by_id(user_id)
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, user: User) -> User:
        """Update user."""
        model = await self._get_by_id(user.id)
        if model:
            model.email = user.email
            model.password_hash = user.password_hash
            model.first_name = user.first_name
            model.last_name = user.last_name
            model.age = user.age
            model.is_active = user.is_active
            model.is_verified = user.is_verified
            model.avatar_url = user.avatar_url
            model.phone_number = user.phone_number
            model.last_login_at = user.last_login_at
            model.updated_at = user.updated_at
            model.nevo_id = user.nevo_id
            model.pin_hash = user.pin_hash
            model.class_code = user.class_code
            await self.session.flush()
            return self._to_entity(model)
        return user

    async def delete(self, user_id: UUID) -> bool:
        """Delete user."""
        return await self._delete(user_id)

    async def list_by_school(
        self,
        school_id: UUID,
        role: Optional[UserRole] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> PaginatedResult[User]:
        """List users by school."""
        query = select(UserModel).where(UserModel.school_id == school_id)

        if role:
            query = query.where(UserModel.role == role)

        query = query.order_by(UserModel.created_at.desc())

        items, total = await self._paginate(query, pagination)

        return PaginatedResult(
            items=[self._to_entity(m) for m in items],
            total=total,
            page=pagination.page if pagination else 1,
            page_size=pagination.page_size if pagination else total,
        )

    async def list_students_by_teacher(
        self,
        teacher_id: UUID,
        pagination: Optional[PaginationParams] = None,
    ) -> PaginatedResult[User]:
        """List students assigned to a teacher."""
        # For MVP, list all students in teacher's school
        teacher = await self.get_by_id(teacher_id)
        if not teacher or not teacher.school_id:
            return PaginatedResult(items=[], total=0, page=1, page_size=20)

        return await self.list_by_school(
            school_id=teacher.school_id,
            role=UserRole.STUDENT,
            pagination=pagination,
        )

    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        result = await self.session.execute(
            select(UserModel.id).where(UserModel.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def get_by_nevo_id(self, nevo_id: str) -> Optional[User]:
        """Get user by Nevo ID."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.nevo_id == nevo_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def exists_by_nevo_id(self, nevo_id: str) -> bool:
        """Check if a Nevo ID already exists."""
        result = await self.session.execute(
            select(UserModel.id).where(UserModel.nevo_id == nevo_id)
        )
        return result.scalar_one_or_none() is not None

    async def get_by_class_code(self, class_code: str) -> Optional[User]:
        """Get teacher by class code."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.class_code == class_code)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def exists_by_class_code(self, class_code: str) -> bool:
        """Check if a class code already exists."""
        result = await self.session.execute(
            select(UserModel.id).where(UserModel.class_code == class_code)
        )
        return result.scalar_one_or_none() is not None
