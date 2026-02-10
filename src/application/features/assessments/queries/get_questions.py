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
        """Get assessment questions matching the UI design (7 questions)."""
        return [
            # Q1: Modality Dominance (Learning Style)
            AssessmentQuestion(
                id=1,
                text="When you're learning something new and you have to choose one, what helps you understand fastest?",
                question_type=QuestionType.SINGLE_CHOICE,
                category="modality_dominance",
                options=[
                    "Seeing diagrams, images, or examples",
                    "Listening to someone explain it",
                    "Trying it out step by step",
                    "Reading it quietly on my own",
                ],
                maps_to_attribute="learning_style",
                order=1,
            ),
            # Q2: Attention Endurance
            AssessmentQuestion(
                id=2,
                text="Before you start feeling restless or mentally tired while learning, what usually happens first?",
                question_type=QuestionType.SINGLE_CHOICE,
                category="attention_endurance",
                options=[
                    "I lose focus quickly",
                    "I get distracted but can refocus",
                    "I stay focused for a while, then fade",
                    "I can stay focused for long periods",
                ],
                maps_to_attribute="attention_span_minutes",
                order=2,
            ),
            # Q3: Difficulty Coping Strategy
            AssessmentQuestion(
                id=3,
                text="When a lesson feels too hard, what do you usually do?",
                question_type=QuestionType.SINGLE_CHOICE,
                category="difficulty_coping",
                options=[
                    "Stop and avoid it",
                    "Push through but feel stressed",
                    "Ask for help or hints",
                    "Take a short break and return",
                ],
                maps_to_attribute="complexity_tolerance",
                order=3,
            ),
            # Q4: Learning Pace Control
            AssessmentQuestion(
                id=4,
                text="Which feels more comfortable when learning?",
                question_type=QuestionType.SINGLE_CHOICE,
                category="learning_pace",
                options=[
                    "Slow and very clear",
                    "Moderate pace with guidance",
                    "Faster pace with challenges",
                    "I like adjusting the pace myself",
                ],
                maps_to_attribute="complexity_tolerance",
                order=4,
            ),
            # Q5: Instruction Structure
            AssessmentQuestion(
                id=5,
                text="What kind of lesson structure helps you most?",
                question_type=QuestionType.SINGLE_CHOICE,
                category="instruction_structure",
                options=[
                    "Short steps with frequent pauses",
                    "One clear explanation, then practice",
                    "Learning by doing immediately",
                    "Exploring freely with minimal instruction",
                ],
                maps_to_attribute="learning_style",
                order=5,
            ),
            # Q6: Feedback Sensitivity
            AssessmentQuestion(
                id=6,
                text="How do you prefer feedback when you make a mistake?",
                question_type=QuestionType.SINGLE_CHOICE,
                category="feedback_sensitivity",
                options=[
                    "Gentle encouragement",
                    "Clear correction right away",
                    "Hints that let me figure it out",
                    "Minimal feedback unless I ask",
                ],
                maps_to_attribute="feedback_preference",
                order=6,
            ),
            # Q7: Environmental Sensitivity
            AssessmentQuestion(
                id=7,
                text="What environment helps you focus best?",
                question_type=QuestionType.SINGLE_CHOICE,
                category="environmental_sensitivity",
                options=[
                    "Quiet and calm",
                    "Light background sound",
                    "Changing activities often",
                    "It depends on my mood",
                ],
                maps_to_attribute="sensory_triggers",
                order=7,
            ),
        ]
