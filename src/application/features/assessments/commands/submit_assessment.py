"""Submit assessment command use case."""

from src.application.common.base_use_case import UseCase
from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.assessments.dtos import (
    SubmitAssessmentInput,
    SubmitAssessmentOutput,
)
from src.core.exceptions import EntityNotFoundError, ValidationError
from src.core.security import generate_nevo_id
from src.domain.entities.assessment import Assessment
from src.domain.entities.neuro_profile import NeuroProfile
from src.domain.interfaces.services import IAIService


class SubmitAssessmentCommand(UseCase[SubmitAssessmentInput, SubmitAssessmentOutput]):
    """Use case for submitting assessment answers and generating profile."""

    def __init__(self, uow: IUnitOfWork, ai_service: IAIService):
        self.uow = uow
        self.ai_service = ai_service

    async def execute(self, input_dto: SubmitAssessmentInput) -> SubmitAssessmentOutput:
        """Submit assessment and trigger profile generation."""
        async with self.uow:
            # Verify student exists
            student = await self.uow.users.get_by_id(input_dto.student_id)
            if not student:
                raise EntityNotFoundError("User", input_dto.student_id)

            if not student.is_student:
                raise ValidationError(
                    message="Only students can complete assessments",
                    field="student_id",
                )

            # Check for existing assessment
            existing = await self.uow.assessments.get_by_student_id(input_dto.student_id)
            if existing and existing.is_complete:
                raise ValidationError(
                    message="Assessment already completed",
                    field="student_id",
                )

            # Create or update assessment
            if existing:
                assessment = existing
            else:
                assessment = Assessment(student_id=input_dto.student_id)

            # Add answers
            for answer in input_dto.answers:
                assessment.add_answer(
                    question_id=answer["question_id"],
                    value=answer["value"],
                )

            assessment.complete()
            assessment.mark_processing()

            if existing:
                await self.uow.assessments.update(assessment)
            else:
                await self.uow.assessments.create(assessment)

            await self.uow.commit()

            # Generate profile asynchronously (in real implementation, use Celery)
            try:
                profile_data = await self.ai_service.generate_student_profile(
                    assessment.get_raw_data()
                )

                # Create or update neuro profile
                existing_profile = await self.uow.neuro_profiles.get_by_user_id(
                    input_dto.student_id
                )

                if existing_profile:
                    existing_profile.update_from_assessment(assessment.get_raw_data())
                    existing_profile.update_generated_profile(profile_data)
                    profile = await self.uow.neuro_profiles.update(existing_profile)
                else:
                    profile = NeuroProfile(
                        user_id=input_dto.student_id,
                        assessment_raw_data=assessment.get_raw_data(),
                    )
                    profile.update_generated_profile(profile_data)
                    profile = await self.uow.neuro_profiles.create(profile)

                assessment.generated_profile_id = profile.id
                await self.uow.assessments.update(assessment)

                # Generate Nevo ID if student doesn't have one
                nevo_id = student.nevo_id
                if not student.has_nevo_id:
                    for _ in range(5):  # Max 5 retries for collision
                        candidate = generate_nevo_id()
                        if not await self.uow.users.exists_by_nevo_id(candidate):
                            student.nevo_id = candidate
                            nevo_id = candidate
                            await self.uow.users.update(student)
                            break

                await self.uow.commit()

                return SubmitAssessmentOutput(
                    status="completed",
                    message="Assessment completed and profile generated",
                    assessment_id=assessment.id,
                    profile_id=profile.id,
                    nevo_id=nevo_id,
                )

            except Exception as e:
                # Log the actual error for debugging
                import logging
                logging.getLogger(__name__).error(
                    "Profile generation failed: %s: %s", type(e).__name__, e,
                    exc_info=True,
                )
                # If AI fails, still save assessment but indicate processing
                return SubmitAssessmentOutput(
                    status="processing",
                    message="Assessment submitted. Profile generation in progress.",
                    assessment_id=assessment.id,
                )
