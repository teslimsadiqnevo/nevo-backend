"""Training data repository implementation."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.domain.entities.training_data import TrainingDataLog
from src.domain.interfaces.repositories import ITrainingDataRepository
from src.infrastructure.database.models.training_data import TrainingDataLogModel
from src.infrastructure.database.repositories.base_repository import BaseRepository


class TrainingDataRepository(BaseRepository[TrainingDataLogModel, TrainingDataLog], ITrainingDataRepository):
    """Training data repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, TrainingDataLogModel)

    def _to_entity(self, model: TrainingDataLogModel) -> TrainingDataLog:
        """Convert model to entity."""
        return TrainingDataLog(
            id=model.id,
            source_id=model.source_id,
            source_type=model.source_type,
            input_context=model.input_context or {},
            model_output=model.model_output or {},
            human_correction=model.human_correction,
            model_name=model.model_name or "",
            model_version=model.model_version or "",
            prompt_template_version=model.prompt_template_version or "",
            metric_score=model.metric_score,
            quality_rating=model.quality_rating,
            was_accepted=model.was_accepted,
            corrected_by_user_id=model.corrected_by_user_id,
            correction_type=model.correction_type,
            correction_notes=model.correction_notes,
            is_processed=model.is_processed,
            processed_at=model.processed_at,
            training_batch_id=model.training_batch_id,
            created_at=model.created_at,
        )

    def _to_model(self, entity: TrainingDataLog) -> TrainingDataLogModel:
        """Convert entity to model."""
        return TrainingDataLogModel(
            id=entity.id,
            source_id=entity.source_id,
            source_type=entity.source_type,
            input_context=entity.input_context,
            model_output=entity.model_output,
            human_correction=entity.human_correction,
            model_name=entity.model_name,
            model_version=entity.model_version,
            prompt_template_version=entity.prompt_template_version,
            metric_score=entity.metric_score,
            quality_rating=entity.quality_rating,
            was_accepted=entity.was_accepted,
            corrected_by_user_id=entity.corrected_by_user_id,
            correction_type=entity.correction_type,
            correction_notes=entity.correction_notes,
            is_processed=entity.is_processed,
            processed_at=entity.processed_at,
            training_batch_id=entity.training_batch_id,
            created_at=entity.created_at,
        )

    async def create(self, log: TrainingDataLog) -> TrainingDataLog:
        """Create a training data log."""
        model = self._to_model(log)
        created = await self._create(model)
        return self._to_entity(created)

    async def get_by_id(self, log_id: UUID) -> Optional[TrainingDataLog]:
        """Get log by ID."""
        model = await self._get_by_id(log_id)
        return self._to_entity(model) if model else None

    async def update(self, log: TrainingDataLog) -> TrainingDataLog:
        """Update log."""
        model = await self._get_by_id(log.id)
        if model:
            model.human_correction = log.human_correction
            model.metric_score = log.metric_score
            model.quality_rating = log.quality_rating
            model.was_accepted = log.was_accepted
            model.corrected_by_user_id = log.corrected_by_user_id
            model.correction_type = log.correction_type
            model.correction_notes = log.correction_notes
            model.is_processed = log.is_processed
            model.processed_at = log.processed_at
            model.training_batch_id = log.training_batch_id
            await self.session.flush()
            return self._to_entity(model)
        return log

    async def list_unprocessed(self, limit: int = 100) -> List[TrainingDataLog]:
        """List unprocessed logs for training."""
        result = await self.session.execute(
            select(TrainingDataLogModel)
            .where(TrainingDataLogModel.is_processed == False)
            .order_by(TrainingDataLogModel.created_at.asc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def list_with_corrections(self, limit: int = 100) -> List[TrainingDataLog]:
        """List logs that have human corrections."""
        result = await self.session.execute(
            select(TrainingDataLogModel)
            .where(
                TrainingDataLogModel.human_correction.isnot(None),
                TrainingDataLogModel.is_processed == False,
            )
            .order_by(TrainingDataLogModel.created_at.asc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def mark_batch_processed(self, log_ids: List[UUID], batch_id: str) -> int:
        """Mark a batch of logs as processed."""
        result = await self.session.execute(
            update(TrainingDataLogModel)
            .where(TrainingDataLogModel.id.in_(log_ids))
            .values(
                is_processed=True,
                processed_at=datetime.utcnow(),
                training_batch_id=batch_id,
            )
        )
        await self.session.flush()
        return result.rowcount
