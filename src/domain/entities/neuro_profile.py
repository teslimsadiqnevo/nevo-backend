"""NeuroProfile entity - The AI context for personalization."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from src.core.config.constants import (
    ComplexityTolerance,
    LearningStyle,
    ReadingLevel,
    SensoryTrigger,
)


@dataclass
class NeuroProfile:
    """
    NeuroProfile entity storing student's learning profile.

    This is the core AI context used for lesson personalization.
    Generated from assessment responses and refined over time.
    """

    user_id: UUID
    id: UUID = field(default_factory=uuid4)

    # Assessment data
    assessment_raw_data: Dict[str, Any] = field(default_factory=dict)

    # Generated profile attributes
    learning_style: LearningStyle = LearningStyle.VISUAL
    reading_level: ReadingLevel = ReadingLevel.GRADE_3
    complexity_tolerance: ComplexityTolerance = ComplexityTolerance.MEDIUM
    attention_span_minutes: int = 15

    # Sensory considerations
    sensory_triggers: List[SensoryTrigger] = field(default_factory=list)

    # Interests and preferences
    interests: List[str] = field(default_factory=list)
    preferred_subjects: List[str] = field(default_factory=list)

    # Additional profile data from AI analysis
    generated_profile: Dict[str, Any] = field(default_factory=dict)

    # Confidence scores (0-1) for profile attributes
    confidence_scores: Dict[str, float] = field(default_factory=dict)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    # Version for tracking profile evolution
    version: int = 1

    def to_ai_context(self) -> Dict[str, Any]:
        """Convert profile to context dictionary for AI prompts."""
        return {
            "learning_style": self.learning_style.value,
            "reading_level": self.reading_level.value,
            "complexity_tolerance": self.complexity_tolerance.value,
            "attention_span_minutes": self.attention_span_minutes,
            "sensory_triggers": [t.value for t in self.sensory_triggers],
            "interests": self.interests,
            "preferred_subjects": self.preferred_subjects,
        }

    def update_from_assessment(self, raw_data: Dict[str, Any]) -> None:
        """Update profile with new assessment data."""
        self.assessment_raw_data = raw_data
        self.last_updated = datetime.utcnow()
        self.version += 1

    def update_generated_profile(self, profile_data: Dict[str, Any]) -> None:
        """Update with AI-generated profile data."""
        self.generated_profile = profile_data

        # Extract specific attributes if present
        if "learning_style" in profile_data:
            try:
                self.learning_style = LearningStyle(profile_data["learning_style"].lower())
            except ValueError:
                pass

        if "complexity_tolerance" in profile_data:
            try:
                self.complexity_tolerance = ComplexityTolerance(
                    profile_data["complexity_tolerance"].lower()
                )
            except ValueError:
                pass

        if "interests" in profile_data:
            self.interests = profile_data["interests"][:10]  # Limit to 10

        self.last_updated = datetime.utcnow()
        self.version += 1
