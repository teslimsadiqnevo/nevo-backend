"""Admin endpoints - Training data monitoring and SLM management."""

from fastapi import APIRouter, Depends

from src.core.config.constants import UserRole
from src.presentation.api.v1.dependencies import get_uow, require_role
from src.application.common.unit_of_work import IUnitOfWork

router = APIRouter()

# Data collection targets (min samples before training is viable)
DATA_TARGETS = {
    "image_prompt": 800,
    "quiz_questions": 1500,
    "chat_response": 3000,
    "lesson_adaptation": 2000,
    "student_profile": 1000,
}


@router.get(
    "/training-data/stats",
    dependencies=[Depends(require_role([UserRole.SCHOOL_ADMIN, UserRole.SUPER_ADMIN]))],
)
async def get_training_data_stats(
    uow: IUnitOfWork = Depends(get_uow),
):
    """Get training data collection statistics for SLM development."""
    counts = await uow.training_data.count_by_source_type()
    unprocessed_logs = await uow.training_data.list_unprocessed(limit=10000)
    total_unprocessed = len(unprocessed_logs)
    # Count only logs where human_correction is a real value (not None/null)
    total_with_corrections = sum(
        1 for log in unprocessed_logs
        if log.human_correction is not None and log.human_correction != {}
    )

    by_task = {}
    for task, target in DATA_TARGETS.items():
        count = counts.get(task, 0)
        by_task[task] = {
            "count": count,
            "target": target,
            "ready": count >= target,
            "progress_pct": min(100, round((count / target) * 100, 1)) if target > 0 else 0,
        }

    return {
        "total_logs": sum(counts.values()),
        "by_task": by_task,
        "unprocessed": total_unprocessed,
        "with_corrections": total_with_corrections,
    }
