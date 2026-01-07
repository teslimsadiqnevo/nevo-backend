"""NeuroProfile repository implementation."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.neuro_profile import NeuroProfile
from src.domain.interfaces.repositories import INeuroProfileRepository
from src.core.config.constants import LearningStyle, ReadingLevel, ComplexityTolerance, SensoryTrigger
from src.infrastructure.database.models.neuro_profile import NeuroProfileModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class NeuroProfileRepository(BaseRepository[NeuroProfileModel, NeuroProfile], INeuroProfileRepository):
    """NeuroProfile repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, NeuroProfileModel)

    def _to_entity(self, model: NeuroProfileModel) -> NeuroProfile:
        """Convert model to entity."""
        # Parse sensory triggers from JSON
        sensory_triggers = []
        for trigger in model.sensory_triggers or []:
            try:
                sensory_triggers.append(SensoryTrigger(trigger))
            except ValueError:
                pass

        return NeuroProfile(
            id=model.id,
            user_id=model.user_id,
            assessment_raw_data=model.assessment_raw_data or {},
            learning_style=model.learning_style,
            reading_level=model.reading_level,
            complexity_tolerance=model.complexity_tolerance,
            attention_span_minutes=model.attention_span_minutes,
            sensory_triggers=sensory_triggers,
            interests=model.interests or [],
            preferred_subjects=model.preferred_subjects or [],
            generated_profile=model.generated_profile or {},
            confidence_scores=model.confidence_scores or {},
            created_at=model.created_at,
            last_updated=model.last_updated or model.updated_at,
            version=model.version,
        )

    def _to_model(self, entity: NeuroProfile) -> NeuroProfileModel:
        """Convert entity to model."""
        return NeuroProfileModel(
            id=entity.id,
            user_id=entity.user_id,
            assessment_raw_data=entity.assessment_raw_data,
            learning_style=entity.learning_style,
            reading_level=entity.reading_level,
            complexity_tolerance=entity.complexity_tolerance,
            attention_span_minutes=entity.attention_span_minutes,
            sensory_triggers=[t.value for t in entity.sensory_triggers],
            interests=entity.interests,
            preferred_subjects=entity.preferred_subjects,
            generated_profile=entity.generated_profile,
            confidence_scores=entity.confidence_scores,
            created_at=entity.created_at,
            last_updated=entity.last_updated,
            version=entity.version,
        )

    async def create(self, profile: NeuroProfile) -> NeuroProfile:
        """Create a new neuro profile."""
        model = self._to_model(profile)
        created = await self._create(model)
        return self._to_entity(created)

    async def get_by_id(self, profile_id: UUID) -> Optional[NeuroProfile]:
        """Get profile by ID."""
        model = await self._get_by_id(profile_id)
        return self._to_entity(model) if model else None

    async def get_by_user_id(self, user_id: UUID) -> Optional[NeuroProfile]:
        """Get profile by user ID."""
        result = await self.session.execute(
            select(NeuroProfileModel).where(NeuroProfileModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, profile: NeuroProfile) -> NeuroProfile:
        """Update profile."""
        model = await self._get_by_id(profile.id)
        if model:
            model.assessment_raw_data = profile.assessment_raw_data
            model.learning_style = profile.learning_style
            model.reading_level = profile.reading_level
            model.complexity_tolerance = profile.complexity_tolerance
            model.attention_span_minutes = profile.attention_span_minutes
            model.sensory_triggers = [t.value for t in profile.sensory_triggers]
            model.interests = profile.interests
            model.preferred_subjects = profile.preferred_subjects
            model.generated_profile = profile.generated_profile
            model.confidence_scores = profile.confidence_scores
            model.last_updated = profile.last_updated
            model.version = profile.version
            await self.session.flush()
            return self._to_entity(model)
        return profile

    async def delete(self, profile_id: UUID) -> bool:
        """Delete profile."""
        return await self._delete(profile_id)
