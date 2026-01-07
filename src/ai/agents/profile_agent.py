"""Profile Generation Agent - Analyzes assessment to create student profiles."""

import json
from typing import Any, Dict

import google.generativeai as genai

from src.ai.prompts.profile_prompts import PROFILE_GENERATION_PROMPT
from src.core.config.settings import settings
from src.core.exceptions import AIServiceError


class ProfileGenerationAgent:
    """
    Agent for generating student neuro-profiles from assessment data.

    Uses Gemini Pro for complex reasoning about learning preferences
    and potential accommodations.
    """

    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(
            settings.gemini_model,
            generation_config={
                "temperature": 0.3,  # Lower temperature for more consistent outputs
                "top_p": 0.8,
                "max_output_tokens": 2048,
            },
        )

    async def generate_profile(
        self,
        assessment_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a student learning profile from assessment responses.

        Args:
            assessment_data: Raw assessment answers from the student

        Returns:
            Generated profile with learning preferences and accommodations
        """
        prompt = PROFILE_GENERATION_PROMPT.format(
            assessment_json=json.dumps(assessment_data, indent=2)
        )

        try:
            response = self.model.generate_content(prompt)
            profile = self._parse_response(response.text)

            # Validate required fields
            self._validate_profile(profile)

            return profile

        except Exception as e:
            raise AIServiceError(
                message=f"Profile generation failed: {str(e)}",
                model=settings.gemini_model,
            )

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from the model response."""
        text = response_text.strip()

        # Remove markdown code blocks if present
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
            # Try to extract JSON object
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            raise ValueError("Could not parse JSON from response")

    def _validate_profile(self, profile: Dict[str, Any]) -> None:
        """Validate profile has required fields."""
        required_fields = [
            "learning_preference",
            "complexity_tolerance",
            "interests",
        ]

        for field in required_fields:
            if field not in profile:
                raise ValueError(f"Missing required field: {field}")

        # Validate enum values
        valid_learning_preferences = ["visual", "auditory", "kinesthetic", "reading_writing"]
        if profile.get("learning_preference", "").lower() not in valid_learning_preferences:
            profile["learning_preference"] = "visual"  # Default

        valid_complexity = ["low", "medium", "high"]
        if profile.get("complexity_tolerance", "").lower() not in valid_complexity:
            profile["complexity_tolerance"] = "medium"  # Default
