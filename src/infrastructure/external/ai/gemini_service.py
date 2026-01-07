"""Google Gemini AI service implementation."""

import json
from typing import Any, Dict, List

import google.generativeai as genai

from src.core.config.settings import settings
from src.core.exceptions import AIServiceError
from src.domain.entities.lesson import Lesson
from src.domain.entities.neuro_profile import NeuroProfile
from src.domain.interfaces.services import IAIService


class GeminiAIService(IAIService):
    """AI service implementation using Google Gemini."""

    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)

    async def generate_student_profile(
        self,
        assessment_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate a student profile from assessment data."""
        prompt = self._build_profile_generation_prompt(assessment_data)

        try:
            response = await self._generate_content(prompt)
            profile = self._parse_json_response(response)

            return {
                "learning_style": profile.get("learning_preference", "visual"),
                "complexity_tolerance": profile.get("complexity_tolerance", "medium"),
                "interests": profile.get("interests", []),
                "attention_span_minutes": profile.get("attention_span_minutes", 15),
                "sensory_triggers": profile.get("sensory_triggers", []),
            }

        except Exception as e:
            raise AIServiceError(
                message=f"Failed to generate profile: {str(e)}",
                model=settings.gemini_model,
            )

    async def adapt_lesson(
        self,
        lesson: Lesson,
        profile: NeuroProfile,
    ) -> Dict[str, Any]:
        """Adapt a lesson for a specific student profile."""
        prompt = self._build_lesson_adaptation_prompt(lesson, profile)

        try:
            response = await self._generate_content(prompt)
            adapted = self._parse_json_response(response)

            return {
                "adaptation_style": adapted.get(
                    "adaptation_style",
                    f"{profile.learning_style.value.title()} Focus"
                ),
                "blocks": adapted.get("blocks", []),
            }

        except Exception as e:
            raise AIServiceError(
                message=f"Failed to adapt lesson: {str(e)}",
                model=settings.gemini_model,
            )

    async def generate_quiz_questions(
        self,
        lesson_content: str,
        profile: NeuroProfile,
        num_questions: int = 3,
    ) -> List[Dict[str, Any]]:
        """Generate quiz questions for a lesson."""
        prompt = f"""Generate {num_questions} quiz questions based on this lesson content.

Student profile:
- Reading level: {profile.reading_level.value}
- Complexity tolerance: {profile.complexity_tolerance.value}

Lesson content:
{lesson_content[:2000]}

Generate questions as a JSON array with this structure:
[
    {{
        "question": "The question text",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_index": 0,
        "explanation": "Brief explanation of the answer"
    }}
]

Make questions appropriate for the student's reading level.
Return ONLY the JSON array, no other text."""

        try:
            response = await self._generate_content(prompt)
            questions = self._parse_json_response(response)
            return questions if isinstance(questions, list) else []

        except Exception as e:
            raise AIServiceError(
                message=f"Failed to generate quiz: {str(e)}",
                model=settings.gemini_model,
            )

    async def generate_image_prompt(
        self,
        concept: str,
        profile: NeuroProfile,
    ) -> str:
        """Generate an image prompt for visual content."""
        prompt = f"""Create a detailed image generation prompt for illustrating this concept:
"{concept}"

For a student who:
- Prefers {profile.learning_style.value} learning
- Has interests in: {', '.join(profile.interests[:3]) if profile.interests else 'general topics'}

The prompt should describe a child-friendly, educational illustration.
Return ONLY the image prompt, no other text."""

        try:
            response = await self._generate_content(prompt)
            return response.strip()

        except Exception as e:
            raise AIServiceError(
                message=f"Failed to generate image prompt: {str(e)}",
                model=settings.gemini_model,
            )

    async def _generate_content(self, prompt: str) -> str:
        """Generate content using Gemini."""
        response = self.model.generate_content(prompt)
        return response.text

    def _parse_json_response(self, response: str) -> Any:
        """Parse JSON from AI response."""
        # Clean up response
        text = response.strip()

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
            # Try to find JSON in the response
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])

            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])

            raise ValueError("Could not parse JSON from response")

    def _build_profile_generation_prompt(self, assessment_data: Dict[str, Any]) -> str:
        """Build the prompt for profile generation."""
        return f"""You are an expert in neurodivergent education. Analyze the following student assessment responses and generate a learning profile.

Assessment Data:
{json.dumps(assessment_data, indent=2)}

Based on these responses, create a JSON profile with these keys:
{{
    "learning_preference": "visual" | "auditory" | "kinesthetic" | "reading_writing",
    "complexity_tolerance": "low" | "medium" | "high",
    "interests": ["list", "of", "interests"],
    "attention_span_minutes": <number 5-30>,
    "sensory_triggers": ["list of triggers if any"]
}}

Rules:
- DO NOT diagnose any medical conditions
- Base analysis only on provided responses
- Be conservative with attention span estimates
- Return ONLY the JSON object, no other text"""

    def _build_lesson_adaptation_prompt(
        self,
        lesson: Lesson,
        profile: NeuroProfile,
    ) -> str:
        """Build the prompt for lesson adaptation."""
        profile_context = profile.to_ai_context()

        return f"""Rewrite the following lesson content for a student with these learning attributes:

Student Profile:
- Learning Style: {profile_context['learning_style']}
- Reading Level: {profile_context['reading_level']}
- Complexity Tolerance: {profile_context['complexity_tolerance']}
- Attention Span: {profile_context['attention_span_minutes']} minutes
- Interests: {', '.join(profile_context['interests'][:5]) if profile_context['interests'] else 'general topics'}
- Sensory Triggers to Avoid: {', '.join(profile_context['sensory_triggers']) if profile_context['sensory_triggers'] else 'none specified'}

Original Lesson Title: {lesson.title}
Original Content:
{lesson.original_text_content[:5000]}

Adaptation Rules:
1. If learning style is 'visual', include detailed imagery descriptions and image prompts
2. If complexity tolerance is 'low', use short sentences, bullet points, and simple vocabulary
3. If complexity tolerance is 'high', can include more detailed explanations
4. Keep content engaging and age-appropriate
5. Include 1-2 quiz questions at the end to check understanding

Output MUST be a valid JSON object with this structure:
{{
    "adaptation_style": "Description of adaptation approach",
    "blocks": [
        {{"type": "heading", "content": "Section title"}},
        {{"type": "text", "content": "Paragraph text", "emphasis": ["key", "words"]}},
        {{"type": "image_prompt", "content": "Description for image generation"}},
        {{"type": "quiz_check", "question": "Question text?", "options": ["A", "B", "C"], "correct_index": 0}}
    ]
}}

Return ONLY the JSON object, no other text."""
