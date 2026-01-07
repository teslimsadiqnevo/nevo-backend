"""Assessment repository implementation."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.assessment import Assessment, AssessmentAnswer
from src.domain.interfaces.repositories import IAssessmentRepository
from src.infrastructure.database.models.assessment import AssessmentModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class AssessmentRepository(BaseRepository[AssessmentModel, Assessment], IAssessmentRepository):
    """Assessment repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, AssessmentModel)

    def _to_entity(self, model: AssessmentModel) -> Assessment:
        """Convert model to entity."""
        answers = [
            AssessmentAnswer(
                question_id=a["question_id"],
                value=a["value"],
            )
            for a in (model.answers or [])
        ]

        return Assessment(
            id=model.id,
            student_id=model.student_id,
            status=model.status,
            answers=answers,
            answers_json=model.answers or [],
            current_question_index=model.current_question_index,
            total_questions=model.total_questions,
            started_at=model.started_at,
            completed_at=model.completed_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            generated_profile_id=model.generated_profile_id,
        )

    def _to_model(self, entity: Assessment) -> AssessmentModel:
        """Convert entity to model."""
        return AssessmentModel(
            id=entity.id,
            student_id=entity.student_id,
            status=entity.status,
            answers=entity.answers_json,
            current_question_index=entity.current_question_index,
            total_questions=entity.total_questions,
            started_at=entity.started_at,
            completed_at=entity.completed_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            generated_profile_id=entity.generated_profile_id,
        )

    async def create(self, assessment: Assessment) -> Assessment:
        """Create a new assessment."""
        model = self._to_model(assessment)
        created = await self._create(model)
        return self._to_entity(created)

    async def get_by_id(self, assessment_id: UUID) -> Optional[Assessment]:
        """Get assessment by ID."""
        model = await self._get_by_id(assessment_id)
        return self._to_entity(model) if model else None

    async def get_by_student_id(self, student_id: UUID) -> Optional[Assessment]:
        """Get assessment by student ID."""
        result = await self.session.execute(
            select(AssessmentModel).where(AssessmentModel.student_id == student_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, assessment: Assessment) -> Assessment:
        """Update assessment."""
        model = await self._get_by_id(assessment.id)
        if model:
            model.status = assessment.status
            model.answers = assessment.answers_json
            model.current_question_index = assessment.current_question_index
            model.total_questions = assessment.total_questions
            model.started_at = assessment.started_at
            model.completed_at = assessment.completed_at
            model.generated_profile_id = assessment.generated_profile_id
            model.updated_at = assessment.updated_at
            await self.session.flush()
            return self._to_entity(model)
        return assessment
