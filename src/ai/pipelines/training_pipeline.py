"""Training Data Pipeline - Prepares data for SLM fine-tuning."""

import json
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from src.domain.entities.training_data import TrainingDataLog


class TrainingDataPipeline:
    """
    Pipeline for processing training data for Small Language Model fine-tuning.

    Converts teacher corrections and interaction data into training format
    suitable for LoRA fine-tuning of models like Llama 3 or Mistral.
    """

    def __init__(self):
        self.batch_id = None

    def start_batch(self) -> str:
        """Start a new training batch."""
        self.batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
        return self.batch_id

    def prepare_training_data(
        self,
        logs: List[TrainingDataLog],
    ) -> Dict[str, Any]:
        """
        Prepare training data from logs.

        Returns data in format suitable for:
        1. Supervised Fine-Tuning (SFT)
        2. Direct Preference Optimization (DPO) for corrections

        Args:
            logs: List of training data logs

        Returns:
            Dictionary with 'sft_data' and 'dpo_data' lists
        """
        sft_data = []
        dpo_data = []

        for log in logs:
            if log.has_correction:
                # Use for DPO (preference learning)
                dpo_sample = self._create_dpo_sample(log)
                if dpo_sample:
                    dpo_data.append(dpo_sample)
            else:
                # Use for SFT if accepted
                if log.was_accepted:
                    sft_sample = self._create_sft_sample(log)
                    if sft_sample:
                        sft_data.append(sft_sample)

        return {
            "batch_id": self.batch_id,
            "created_at": datetime.utcnow().isoformat(),
            "sft_data": sft_data,
            "dpo_data": dpo_data,
            "stats": {
                "total_samples": len(sft_data) + len(dpo_data),
                "sft_samples": len(sft_data),
                "dpo_samples": len(dpo_data),
            },
        }

    def _create_sft_sample(self, log: TrainingDataLog) -> Dict[str, Any]:
        """Create a supervised fine-tuning sample."""
        try:
            return {
                "id": str(log.id),
                "instruction": self._extract_instruction(log.input_context),
                "input": json.dumps(log.input_context),
                "output": json.dumps(log.model_output),
                "metadata": {
                    "source_type": log.source_type,
                    "model": log.model_name,
                    "quality_score": log.metric_score,
                },
            }
        except Exception:
            return None

    def _create_dpo_sample(self, log: TrainingDataLog) -> Dict[str, Any]:
        """Create a DPO (preference) training sample."""
        try:
            return {
                "id": str(log.id),
                "prompt": self._extract_instruction(log.input_context),
                "input_context": json.dumps(log.input_context),
                "chosen": json.dumps(log.human_correction),  # Teacher's correction
                "rejected": json.dumps(log.model_output),  # Original AI output
                "metadata": {
                    "source_type": log.source_type,
                    "correction_type": log.correction_type,
                    "corrector_id": str(log.corrected_by_user_id) if log.corrected_by_user_id else None,
                },
            }
        except Exception:
            return None

    def _extract_instruction(self, input_context: Dict[str, Any]) -> str:
        """Extract or generate instruction from input context."""
        # Try to get instruction from context
        if "instruction" in input_context:
            return input_context["instruction"]

        # Generate instruction based on context type
        if "block_type" in input_context:
            block_type = input_context["block_type"]
            return f"Generate adapted {block_type} content for a student"

        if "profile" in input_context:
            return "Adapt the following lesson content for the student profile"

        return "Generate educational content"

    def export_to_jsonl(
        self,
        data: Dict[str, Any],
        output_path: str,
    ) -> None:
        """Export training data to JSONL format."""
        with open(output_path, "w") as f:
            # Export SFT data
            for sample in data.get("sft_data", []):
                f.write(json.dumps(sample) + "\n")

    def export_dpo_to_jsonl(
        self,
        data: Dict[str, Any],
        output_path: str,
    ) -> None:
        """Export DPO data to JSONL format."""
        with open(output_path, "w") as f:
            for sample in data.get("dpo_data", []):
                f.write(json.dumps(sample) + "\n")

    def get_training_stats(
        self,
        logs: List[TrainingDataLog],
    ) -> Dict[str, Any]:
        """Get statistics about available training data."""
        total = len(logs)
        with_corrections = sum(1 for log in logs if log.has_correction)
        accepted = sum(1 for log in logs if log.was_accepted and not log.has_correction)

        correction_types = {}
        for log in logs:
            if log.correction_type:
                correction_types[log.correction_type] = correction_types.get(log.correction_type, 0) + 1

        return {
            "total_logs": total,
            "with_corrections": with_corrections,
            "accepted_without_changes": accepted,
            "correction_types": correction_types,
            "ready_for_dpo": with_corrections,
            "ready_for_sft": accepted,
        }
