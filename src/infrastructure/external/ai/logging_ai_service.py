"""Logging AI Service decorator - captures all AI interactions for SLM training."""

import logging
import time
from typing import Any, Dict, List, Optional
from uuid import uuid4

from src.domain.entities.lesson import Lesson
from src.domain.entities.neuro_profile import NeuroProfile
from src.domain.entities.training_data import TrainingDataLog
from src.domain.interfaces.services import IAIService
from src.infrastructure.database.session import AsyncSessionLocal
from src.infrastructure.database.repositories.training_data_repository import TrainingDataRepository

logger = logging.getLogger(__name__)


class LoggingAIService(IAIService):
    """Decorator that wraps any IAIService to log all interactions for SLM training data."""

    def __init__(self, inner_service: IAIService):
        self._inner = inner_service

    async def _log_interaction(
        self,
        source_type: str,
        input_context: Dict[str, Any],
        model_output: Any,
        model_name: str,
        duration_ms: int,
    ) -> None:
        """Log an AI interaction to the training_data_logs table."""
        try:
            # Normalize model_output to dict
            if isinstance(model_output, str):
                output_data = {"text": model_output}
            elif isinstance(model_output, list):
                output_data = {"items": model_output}
            elif isinstance(model_output, dict):
                output_data = model_output
            else:
                output_data = {"raw": str(model_output)}

            log = TrainingDataLog(
                source_id=uuid4(),
                source_type=source_type,
                input_context=input_context,
                model_output=output_data,
                model_name=model_name,
                was_accepted=True,
            )

            async with AsyncSessionLocal() as session:
                repo = TrainingDataRepository(session)
                await repo.create(log)
                await session.commit()

        except Exception as e:
            # Never let logging failures break the AI service
            logger.warning(f"Failed to log AI interaction ({source_type}): {e}")

    def _get_model_name(self) -> str:
        """Get the model name from the inner service."""
        return getattr(self._inner, "model_name", "unknown")

    def _profile_to_context(self, profile: NeuroProfile) -> Dict[str, Any]:
        """Convert a NeuroProfile to a serializable dict for logging."""
        try:
            return profile.to_ai_context()
        except Exception:
            return {
                "learning_style": str(getattr(profile, "learning_style", "")),
                "interests": getattr(profile, "interests", []),
            }

    async def generate_student_profile(
        self,
        assessment_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate a student profile, logging the interaction."""
        start = time.time()
        result = await self._inner.generate_student_profile(assessment_data)
        duration_ms = int((time.time() - start) * 1000)

        await self._log_interaction(
            source_type="student_profile",
            input_context={
                "task": "generate_student_profile",
                "assessment_data": assessment_data,
            },
            model_output=result,
            model_name=self._get_model_name(),
            duration_ms=duration_ms,
        )
        return result

    async def adapt_lesson(
        self,
        lesson: Lesson,
        profile: NeuroProfile,
    ) -> Dict[str, Any]:
        """Adapt a lesson, logging the interaction."""
        start = time.time()
        result = await self._inner.adapt_lesson(lesson, profile)
        duration_ms = int((time.time() - start) * 1000)

        await self._log_interaction(
            source_type="lesson_adaptation",
            input_context={
                "task": "adapt_lesson",
                "lesson_title": lesson.title,
                "lesson_content": (lesson.original_text_content or "")[:5000],
                "profile": self._profile_to_context(profile),
            },
            model_output=result,
            model_name=self._get_model_name(),
            duration_ms=duration_ms,
        )
        return result

    async def generate_quiz_questions(
        self,
        lesson_content: str,
        profile: NeuroProfile,
        num_questions: int = 3,
    ) -> List[Dict[str, Any]]:
        """Generate quiz questions, logging the interaction."""
        start = time.time()
        result = await self._inner.generate_quiz_questions(lesson_content, profile, num_questions)
        duration_ms = int((time.time() - start) * 1000)

        await self._log_interaction(
            source_type="quiz_questions",
            input_context={
                "task": "generate_quiz_questions",
                "lesson_content": lesson_content[:2000],
                "profile": self._profile_to_context(profile),
                "num_questions": num_questions,
            },
            model_output=result,
            model_name=self._get_model_name(),
            duration_ms=duration_ms,
        )
        return result

    async def generate_image_prompt(
        self,
        concept: str,
        profile: NeuroProfile,
    ) -> str:
        """Generate an image prompt, logging the interaction."""
        start = time.time()
        result = await self._inner.generate_image_prompt(concept, profile)
        duration_ms = int((time.time() - start) * 1000)

        await self._log_interaction(
            source_type="image_prompt",
            input_context={
                "task": "generate_image_prompt",
                "concept": concept,
                "profile": self._profile_to_context(profile),
            },
            model_output=result,
            model_name=self._get_model_name(),
            duration_ms=duration_ms,
        )
        return result

    async def generate_chat_response(
        self,
        question: str,
        profile: NeuroProfile,
        chat_history: List[Dict[str, str]],
        lesson_context: Optional[str] = None,
    ) -> str:
        """Generate a chat response, logging the interaction."""
        start = time.time()
        result = await self._inner.generate_chat_response(
            question, profile, chat_history, lesson_context
        )
        duration_ms = int((time.time() - start) * 1000)

        await self._log_interaction(
            source_type="chat_response",
            input_context={
                "task": "generate_chat_response",
                "question": question,
                "profile": self._profile_to_context(profile),
                "chat_history": chat_history[-10:],
                "lesson_context": (lesson_context or "")[:2000],
            },
            model_output=result,
            model_name=self._get_model_name(),
            duration_ms=duration_ms,
        )
        return result
