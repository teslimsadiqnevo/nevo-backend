"""Prompts for lesson adaptation."""

LESSON_ADAPTATION_PROMPT = """You are an expert educational content adapter specializing in personalized learning. Your task is to transform lesson content for a specific student.

## Student Learning Profile
- Learning Style: {learning_style}
- Reading Level: {reading_level}
- Complexity Tolerance: {complexity_tolerance}
- Attention Span: {attention_span} minutes
- Interests: {interests}
- Sensory Triggers to Avoid: {sensory_triggers}

## Original Lesson
Title: {lesson_title}

Content:
{lesson_content}

## Adaptation Rules

### For VISUAL Learners:
- Include detailed imagery descriptions
- Add image prompts for key concepts
- Use diagrams and visual metaphors
- Break text into visually distinct sections

### For AUDITORY Learners:
- Include rhythm and patterns in explanations
- Suggest read-aloud sections
- Use conversational tone
- Include mnemonic devices

### For KINESTHETIC Learners:
- Include hands-on activities
- Add movement-based learning suggestions
- Use action verbs and physical metaphors
- Include "try this" exercises

### For READING/WRITING Learners:
- Provide detailed written explanations
- Include note-taking prompts
- Add vocabulary highlights
- Suggest writing exercises

### Complexity Adjustments:
- LOW: Short sentences, simple vocabulary, bullet points, one concept at a time
- MEDIUM: Balanced explanations, some technical terms with definitions
- HIGH: Detailed explanations, advanced vocabulary, complex connections

### Attention Span Considerations:
- Break content into chunks that fit within attention span
- Add engagement checkpoints
- Include brief activities between sections

## Required Output Format
Return a JSON object with this EXACT structure:
{{
    "adaptation_style": "Brief description of adaptation approach used",
    "blocks": [
        {{
            "type": "heading",
            "content": "Section title"
        }},
        {{
            "type": "text",
            "content": "Adapted paragraph text",
            "emphasis": ["key", "words", "to", "highlight"]
        }},
        {{
            "type": "image_prompt",
            "content": "Detailed description for image generation"
        }},
        {{
            "type": "quiz_check",
            "question": "Quick comprehension check question?",
            "options": ["Option A", "Option B", "Option C"],
            "correct_index": 0
        }},
        {{
            "type": "activity",
            "content": "Brief hands-on or thinking activity"
        }},
        {{
            "type": "summary",
            "content": "Key takeaways from this section"
        }}
    ]
}}

## Content Block Types Available:
- "heading": Section headers
- "text": Paragraph content (can include "emphasis" array)
- "image_prompt": Description for visual generation
- "quiz_check": Quick understanding check (include question, options, correct_index)
- "activity": Interactive element or exercise
- "summary": Key points summary

## Guidelines:
1. Start with an engaging heading
2. Keep paragraphs short and focused
3. Add at least one image prompt for visual concepts
4. Include 1-2 quiz checks to verify understanding
5. End with a summary of key points
6. Total content should fit within the attention span
7. Use the student's interests to make examples relatable
8. Avoid any sensory triggers mentioned

Return ONLY the JSON object, no additional text."""


QUIZ_GENERATION_PROMPT = """Generate {num_questions} quiz questions for the following lesson content.

## Student Profile
- Reading Level: {reading_level}
- Complexity Tolerance: {complexity_tolerance}

## Lesson Content
{lesson_content}

## Requirements
- Questions should test understanding, not memorization
- Difficulty should match the complexity tolerance
- Language should match the reading level
- Include a mix of question types if possible
- Each question should have 3-4 options
- Include brief explanations for correct answers

## Output Format
Return a JSON array:
[
    {{
        "question": "Clear question text?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_index": 0,
        "explanation": "Why this answer is correct",
        "difficulty": "easy" | "medium" | "hard"
    }}
]

Return ONLY the JSON array."""
