"""Get assessment questions query."""

from typing import List

from src.application.features.assessments.dtos import GetQuestionsOutput, QuestionDTO
from src.core.config.constants import QuestionType
from src.domain.entities.assessment import AssessmentQuestion


class GetQuestionsQuery:
    """Query to get assessment questions."""

    def __init__(self):
        # In production, these would come from a database or configuration
        self.questions = self._get_default_questions()

    async def execute(self) -> GetQuestionsOutput:
        """Get all assessment questions."""
        question_dtos = [
            QuestionDTO(
                id=q.id,
                text=q.text,
                type=q.question_type.value,
                category=q.category,
                options=q.options,
                scale_min=q.scale_min,
                scale_max=q.scale_max,
                is_required=q.is_required,
                order=q.order,
            )
            for q in self.questions
        ]

        categories = list(set(q.category for q in self.questions))

        return GetQuestionsOutput(
            questions=question_dtos,
            total_questions=len(question_dtos),
            categories=categories,
        )

    def _get_default_questions(self) -> List[AssessmentQuestion]:
        """Get default assessment questions for MVP."""
        return [
            # Learning Style Questions
            AssessmentQuestion(
                id=1,
                text="How do you prefer to learn new things?",
                question_type=QuestionType.SINGLE_CHOICE,
                category="learning_style",
                options=[
                    "Watching videos or looking at pictures",
                    "Listening to explanations",
                    "Doing activities and hands-on practice",
                    "Reading and writing notes",
                ],
                maps_to_attribute="learning_style",
                order=1,
            ),
            AssessmentQuestion(
                id=2,
                text="When you remember something, what helps you most?",
                question_type=QuestionType.SINGLE_CHOICE,
                category="learning_style",
                options=[
                    "Pictures or diagrams in my mind",
                    "The sound of someone explaining it",
                    "The feeling of doing it myself",
                    "Words and sentences I read",
                ],
                maps_to_attribute="learning_style",
                order=2,
            ),
            # Sensory Questions
            AssessmentQuestion(
                id=3,
                text="What makes it hard for you to focus?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category="sensory",
                options=[
                    "Loud noises",
                    "Bright or flashing lights",
                    "Too many things on the screen",
                    "Things moving too fast",
                    "None of these bother me",
                ],
                maps_to_attribute="sensory_triggers",
                order=3,
            ),
            # Attention Questions
            AssessmentQuestion(
                id=4,
                text="How long can you focus on a lesson before needing a break?",
                question_type=QuestionType.SINGLE_CHOICE,
                category="attention",
                options=[
                    "About 5 minutes",
                    "About 10 minutes",
                    "About 15-20 minutes",
                    "More than 20 minutes",
                ],
                maps_to_attribute="attention_span_minutes",
                order=4,
            ),
            # Complexity Questions
            AssessmentQuestion(
                id=5,
                text="What kind of explanations do you like best?",
                question_type=QuestionType.SINGLE_CHOICE,
                category="complexity",
                options=[
                    "Short and simple with pictures",
                    "Medium length with some examples",
                    "Detailed with lots of information",
                ],
                maps_to_attribute="complexity_tolerance",
                order=5,
            ),
            # Interest Questions
            AssessmentQuestion(
                id=6,
                text="What topics do you enjoy learning about?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                category="interests",
                options=[
                    "Science and nature",
                    "Stories and reading",
                    "Math and numbers",
                    "Art and creativity",
                    "Sports and movement",
                    "Music and sounds",
                    "Technology and computers",
                    "History and people",
                ],
                maps_to_attribute="interests",
                order=6,
            ),
            # Reading Level Assessment
            AssessmentQuestion(
                id=7,
                text="Which sentence is easiest for you to read?",
                question_type=QuestionType.SINGLE_CHOICE,
                category="reading_level",
                options=[
                    "The cat sat on the mat.",
                    "The curious kitten explored the garden.",
                    "The inquisitive feline investigated its surroundings thoroughly.",
                    "The perspicacious cat demonstrated remarkable environmental awareness.",
                ],
                maps_to_attribute="reading_level",
                order=7,
            ),
            # Confidence Question
            AssessmentQuestion(
                id=8,
                text="How do you feel about trying new or difficult things?",
                question_type=QuestionType.SCALE,
                category="confidence",
                scale_min=1,
                scale_max=5,
                order=8,
            ),
        ]
