"""Lesson Adaptation Agent - Personalizes lessons for students."""

import json
from typing import Any, Dict, List

from google import genai
from google.genai import types

from src.ai.prompts.adaptation_prompts import LESSON_ADAPTATION_PROMPT
from src.core.config.settings import settings
from src.core.exceptions import AIServiceError
from src.domain.entities.lesson import Lesson
from src.domain.entities.neuro_profile import NeuroProfile


class LessonAdaptationAgent:
    """
    Agent for adapting lessons to individual student profiles.

    Transforms original lesson content into personalized content blocks
    based on the student's learning style, reading level, and preferences.
    """

    def __init__(self):
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model_name = settings.gemini_model
        self.config = types.GenerateContentConfig(
            temperature=0.7,  # Some creativity for engaging content
            top_p=0.9,
            max_output_tokens=4096,
        )

    async def adapt_lesson(
        self,
        lesson: Lesson,
        profile: NeuroProfile,
    ) -> Dict[str, Any]:
        """
        Adapt a lesson for a specific student profile.

        Args:
            lesson: Original lesson content
            profile: Student's neuro profile

        Returns:
            Adapted lesson with content blocks
        """
        profile_context = profile.to_ai_context()

        prompt = LESSON_ADAPTATION_PROMPT.format(
            learning_style=profile_context["learning_style"],
            reading_level=profile_context["reading_level"],
            complexity_tolerance=profile_context["complexity_tolerance"],
            attention_span=profile_context["attention_span_minutes"],
            interests=", ".join(profile_context["interests"][:5]) if profile_context["interests"] else "general topics",
            sensory_triggers=", ".join(profile_context["sensory_triggers"]) if profile_context["sensory_triggers"] else "none specified",
            lesson_title=lesson.title,
            lesson_content=lesson.original_text_content[:5000],  # Limit content length
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.config,
            )
            adapted = self._parse_response(response.text)

            # Validate and sanitize blocks
            adapted["blocks"] = self._validate_blocks(adapted.get("blocks", []))

            return adapted

        except Exception as e:
            raise AIServiceError(
                message=f"Lesson adaptation failed: {str(e)}",
                model=self.model_name,
            )

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from the model response."""
        text = response_text.strip()

        # Remove markdown code blocks
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            raise ValueError("Could not parse JSON from response")

    def _validate_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and sanitize content blocks."""
        valid_types = ["heading", "text", "image", "image_prompt", "quiz", "quiz_check", "activity", "summary"]
        validated = []

        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue

            block_type = block.get("type", "text")
            if block_type not in valid_types:
                block_type = "text"

            validated_block = {
                "id": block.get("id", str(i)),
                "type": block_type,
                "content": block.get("content", ""),
                "order": i,
            }

            # Add type-specific fields
            if block_type == "text" and "emphasis" in block:
                validated_block["emphasis"] = block["emphasis"]

            if block_type in ["image", "image_prompt"] and "ai_generated_url" in block:
                validated_block["ai_generated_url"] = block["ai_generated_url"]

            if block_type in ["quiz", "quiz_check"]:
                validated_block["question"] = block.get("question", block.get("content", ""))
                validated_block["options"] = block.get("options", [])
                validated_block["correct_index"] = block.get("correct_index", 0)

            validated.append(validated_block)

        return validated
