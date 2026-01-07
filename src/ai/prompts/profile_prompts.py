"""Prompts for student profile generation."""

PROFILE_GENERATION_PROMPT = """You are an expert in neurodivergent education and learning sciences. Your task is to analyze student assessment responses and generate a comprehensive learning profile.

## Assessment Data
```json
{assessment_json}
```

## Your Task
Analyze these responses carefully and create a learning profile. Consider:
1. How the student prefers to receive information
2. Their comfort level with complexity
3. Potential sensory sensitivities
4. Attention and focus patterns
5. Areas of interest that can be leveraged for engagement

## Important Guidelines
- DO NOT diagnose any medical or psychological conditions
- Base your analysis ONLY on the provided responses
- Be conservative with estimates when uncertain
- Focus on actionable learning preferences, not labels
- Consider that students may have multiple learning preferences

## Required Output Format
Return a JSON object with EXACTLY this structure:
{{
    "learning_preference": "visual" | "auditory" | "kinesthetic" | "reading_writing",
    "complexity_tolerance": "low" | "medium" | "high",
    "interests": ["list", "of", "interests", "from", "responses"],
    "attention_span_minutes": <number between 5 and 30>,
    "sensory_triggers": ["list of triggers if mentioned, empty array if none"],
    "recommended_adaptations": [
        "Specific adaptation recommendation 1",
        "Specific adaptation recommendation 2"
    ],
    "engagement_strategies": [
        "Strategy to keep student engaged 1",
        "Strategy to keep student engaged 2"
    ],
    "confidence_notes": "Brief note about confidence level in this assessment"
}}

Return ONLY the JSON object, no additional text or explanation."""


PROFILE_REFINEMENT_PROMPT = """You are refining a student's learning profile based on new interaction data.

## Current Profile
```json
{current_profile}
```

## New Interaction Data
```json
{interaction_data}
```

## Task
Update the profile based on how the student actually performed and engaged.
Consider:
- Did they complete tasks faster/slower than expected?
- Which content types did they engage with most?
- Were there any struggles or exceptional successes?

Return an updated profile JSON with the same structure, adjusting values based on observed behavior.
Only make changes supported by the interaction data."""
