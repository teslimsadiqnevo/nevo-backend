# Nevo SLM (Small Language Model) - Full Roadmap

> **Vision:** Over the next 2 years, build Nevo's own Small Language Model that learns from current Gemini AI interactions and progressively replaces all external AI dependencies.

> **Status:** Phase 1 COMPLETE. Gemini is the active AI provider, all interactions are being logged to `training_data_logs` for future SLM fine-tuning.

---

## Table of Contents

- [Why We're Building This](#why-were-building-this)
- [What Already Exists](#what-already-exists)
- [The 5 AI Tasks](#the-5-ai-tasks-ranked-by-complexity)
- [Phase 1: Data Collection Layer](#phase-1-data-collection-layer) -- **COMPLETE**
- [Phase 2: SLM Training Pipeline](#phase-2-slm-training-pipeline-weeks-5-12)
- [Phase 3: Deploy SLM for 2 Tasks](#phase-3-deploy-slm-for-2-tasks-weeks-13-18)
- [Phase 4: Quality Assurance & Evaluation](#phase-4-quality-assurance--evaluation-weeks-16-22)
- [Phase 5: Expansion to All 5 Tasks](#phase-5-expansion-roadmap-months-8-24)
- [Architecture Diagrams](#architecture-diagrams)
- [Timeline Summary](#timeline-summary)

---

## Why We're Building This

Nevo currently depends entirely on Google Gemini for all AI tasks:

1. Generating student NeuroProfiles from assessments
2. Adapting lessons to individual learning styles
3. Generating quiz questions
4. Creating image prompts for visual content
5. Powering the Nevo AI tutor chat

**Problems with full Gemini dependency:**

| Problem | Impact |
|---------|--------|
| **Single point of failure** | If Google changes pricing, rate-limits, or deprecates the API, Nevo's core features break |
| **Ongoing API costs** | Every student interaction costs money that scales linearly with usage |
| **Zero control** | Can't fine-tune Gemini's behavior for Nevo's specific educational context |
| **Data privacy** | All student data flows through Google's servers |
| **Latency** | Every AI call requires a round-trip to Google's API (8-30 seconds per call) |

**The SLM solves all of these:** A self-hosted model trained on Nevo's own data gives us full control, predictable costs, lower latency, and data sovereignty.

---

## What Already Exists

The codebase already has significant infrastructure ready for this transition:

| Component | File | Status |
|-----------|------|--------|
| `TrainingDataLog` entity | `src/domain/entities/training_data.py` | Built -- has `input_context`, `model_output`, `human_correction`, `to_training_format()`, DPO support |
| `TrainingDataLogModel` DB model | `src/infrastructure/database/models/training_data.py` | Built -- full schema with `is_processed`, `training_batch_id` |
| `TrainingDataRepository` | `src/infrastructure/database/repositories/training_data_repository.py` | Built -- CRUD, `list_unprocessed`, `list_with_corrections`, `mark_batch_processed` |
| `ITrainingDataRepository` interface | `src/domain/interfaces/repositories.py` | Built |
| `TrainingDataPipeline` | `src/ai/pipelines/training_pipeline.py` | Built -- SFT + DPO data preparation, JSONL export, batch management |
| `IAIService` interface | `src/domain/interfaces/services.py` | Built -- 5 abstract methods, clean contract |
| `GeminiAIService` | `src/infrastructure/external/ai/gemini_service.py` | Built -- all 5 AI methods implemented |
| `OllamaAIService` | `src/infrastructure/external/ai/ollama_service.py` | Built -- proves pluggable AI backends work |
| Dependency injection | `src/presentation/api/v1/dependencies/services.py` | Built -- `get_ai_service()` switches between Gemini/Ollama |

**Phase 1 Status:** `LoggingAIService` decorator now wraps `GeminiAIService` and logs every AI call to `training_data_logs`. Data is actively being collected.

---

## The 5 AI Tasks (Ranked by Complexity)

| Rank | Task | Method | Input | Output | Reasoning % | SLM Target |
|------|------|--------|-------|--------|-------------|------------|
| 1 | Image Prompts | `generate_image_prompt` | concept + profile | Plain text | 30% (pattern matching) | Phase 3 |
| 2 | Quiz Questions | `generate_quiz_questions` | lesson + profile + count | JSON array | 50% (extraction) | Phase 3 |
| 3 | Chat Response | `generate_chat_response` | question + profile + 10-msg history + lesson context | Plain text | 40% (conversation) | Phase 5a |
| 4 | Lesson Adaptation | `adapt_lesson` | lesson + 6-attribute profile | Multi-block JSON (heading, text, image_prompt, quiz_check, activity, summary) | 70% (transformation) | Phase 5b |
| 5 | Student Profile | `generate_student_profile` | 7 Q&A assessment answers | Structured profile JSON (8 fields) | 80% (expert reasoning) | Phase 5c |

### Why Start With Tasks 1 and 2?

**`generate_image_prompt`** is the simplest AI task in Nevo:
- Input: A concept string + student's learning style and interests
- Output: A single text string describing an image
- No JSON parsing needed
- Low stakes -- a slightly different image prompt doesn't break the learning experience
- The Gemini prompt is only ~6 lines

**`generate_quiz_questions`** is the next simplest:
- Input: Lesson text + reading level + number of questions
- Output: JSON array with fixed schema (question, options, correct_index, explanation)
- Schema is strict and validatable -- easy to check if SLM output is correct
- Moderate stakes -- wrong answers can be caught by schema validation
- Clear training signal: either the JSON is valid or it isn't

---

## Phase 1: Data Collection Layer -- COMPLETE

> **Status: COMPLETE** (implemented 2026-02-27)
> **Timeline: Weeks 1-4**
> **Goal:** Automatically log every Gemini AI call (input + output) into `training_data_logs`. This creates the training dataset for the SLM.

### 1.1 LoggingAIService Decorator

**Create:** `src/infrastructure/external/ai/logging_ai_service.py`

A decorator/wrapper that wraps any `IAIService` implementation and logs every call transparently. Zero changes needed to `GeminiAIService` or `OllamaAIService`.

```
Request Flow (Before):
  Endpoint -> GeminiAIService -> Gemini API -> Response

Request Flow (After):
  Endpoint -> LoggingAIService -> GeminiAIService -> Gemini API -> Response
                |                                                    |
                +-- logs input_context to training_data_logs ---------+-- logs model_output
```

Each of the 5 methods gets logged with a distinct `source_type`:

| Method | source_type | What's Captured in input_context | What's Captured in model_output |
|--------|-------------|--------------------------------|-------------------------------|
| `generate_image_prompt` | `"image_prompt"` | concept, learning_style, interests | The prompt text |
| `generate_quiz_questions` | `"quiz_questions"` | lesson_content (truncated), reading_level, complexity_tolerance, num_questions | JSON array of questions |
| `generate_chat_response` | `"chat_response"` | question, learning_style, reading_level, chat_history, lesson_context | Response text |
| `adapt_lesson` | `"lesson_adaptation"` | lesson_title, lesson_content, full profile context | adaptation_style + blocks JSON |
| `generate_student_profile` | `"student_profile"` | assessment_data (7 Q&A) | Generated profile JSON |

### 1.2 New Settings

**Modify:** `src/core/config/settings.py`

```python
# AI Data Collection
ai_logging_enabled: bool = Field(default=True, description="Log AI interactions for SLM training")
```

### 1.3 Updated Dependency Injection

**Modify:** `src/presentation/api/v1/dependencies/services.py`

```python
def get_ai_service() -> IAIService:
    if settings.local_ai_enabled:
        inner = OllamaAIService()
    else:
        inner = GeminiAIService()

    if settings.ai_logging_enabled:
        return LoggingAIService(inner)
    return inner
```

### 1.4 Training Data Repository Enhancements

**Modify:** `src/infrastructure/database/repositories/training_data_repository.py`

Add two new methods:
- `list_by_source_type(source_type: str, limit: int) -> List[TrainingDataLog]` -- filter by task type for task-specific training
- `count_by_source_type() -> Dict[str, int]` -- returns `{"image_prompt": 234, "quiz_questions": 89, ...}` for monitoring collection progress

### 1.5 Admin Dashboard Endpoint

**Create:** `src/presentation/api/v1/endpoints/admin.py`

```
GET /api/v1/admin/training-data/stats

Response:
{
  "total_logs": 1523,
  "by_task": {
    "image_prompt": {"count": 456, "ready": true, "target": 800},
    "quiz_questions": {"count": 234, "ready": false, "target": 1500},
    "chat_response": {"count": 678, "ready": false, "target": 3000},
    "lesson_adaptation": {"count": 123, "ready": false, "target": 2000},
    "student_profile": {"count": 32, "ready": false, "target": 1000}
  },
  "unprocessed": 1523,
  "with_corrections": 0
}
```

### Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| **Create** | `src/infrastructure/external/ai/logging_ai_service.py` | Decorator that logs all AI calls |
| **Create** | `src/presentation/api/v1/endpoints/admin.py` | Training data stats endpoint |
| **Modify** | `src/presentation/api/v1/dependencies/services.py` | Wire LoggingAIService into DI |
| **Modify** | `src/core/config/settings.py` | Add `ai_logging_enabled` setting |
| **Modify** | `src/infrastructure/database/repositories/training_data_repository.py` | Add source_type filtering |
| **Modify** | `src/presentation/api/v1/router.py` | Register admin endpoints |
| **Modify** | `.env` | Add `AI_LOGGING_ENABLED=true` |

### Data Collection Targets

| Task | Min Samples Needed | Estimated Collection Time | Notes |
|------|-------------------|--------------------------|-------|
| `image_prompt` | ~800 | 2-3 months | Generated during lesson adaptation |
| `quiz_questions` | ~1,500 | 3-4 months | Generated during lesson adaptation |
| `chat_response` | ~3,000 | 4-6 months | Every student chat interaction |
| `lesson_adaptation` | ~2,000 | 6-8 months | Each unique lesson+student pair |
| `student_profile` | ~1,000 | 8-12 months | One per new student assessment |

### Verification

- [x] Submit an assessment -> confirmed `training_data_logs` row with `source_type="student_profile"` (1 sample)
- [x] Play a lesson -> confirmed row with `source_type="lesson_adaptation"` (1 sample)
- [x] Chat with Nevo -> confirmed rows with `source_type="chat_response"` (19 samples)
- [x] Hit `GET /api/v1/admin/training-data/stats` -> returns counts per task (admin-only)
- [x] All existing AI features continue working unchanged (load test: 20/20 pass)

---

## Phase 2: SLM Training Pipeline (Weeks 5-12)

> **Status: NOT STARTED**
> **Depends on:** Phase 1 collecting data for 2+ months

### 2.1 Base Model Selection

**Primary: Qwen 2.5-3B-Instruct**

| Criteria | Qwen 2.5-3B | Phi-3.5-mini (3.8B) | Llama 3.2-3B |
|----------|------------|-------------------|-------------|
| JSON output quality | Excellent | Good | Good |
| Instruction following | Excellent | Good | Good |
| Memory (inference) | ~6GB | ~7.5GB | ~6GB |
| LoRA fine-tuning VRAM | ~8GB | ~10GB | ~8GB |
| License | Apache 2.0 | MIT | Llama License |

Qwen 2.5-3B wins on JSON reliability (critical for `generate_quiz_questions`) and runs on a single 8GB GPU. For Phase 5's more complex tasks, we'll upgrade to a 7B variant.

### 2.2 Training Architecture

```
Training Data Flow:

  training_data_logs (PostgreSQL)
         |
         v
  TrainingDataPipeline.prepare_training_data()  [already exists]
         |
         v
  TaskDataFormatter (image_prompt / quiz_questions)  [new]
         |
         v
  HuggingFace Dataset (chat template format)
         |
         v
  SFTTrainer + LoRA (r=16, alpha=32)  [new]
         |
         v
  LoRA Adapter weights (saved to disk)
         |
         v
  Evaluation on 10% held-out test set  [new]
```

### 2.3 Fine-Tuning Pipeline

**Create:** `src/ai/training/fine_tuning_pipeline.py`

```python
class FineTuningPipeline:
    def __init__(self, base_model: str, task_type: str):
        ...

    def prepare_dataset(self, raw_data: List[Dict]) -> Dataset:
        """Convert training logs into chat-template format."""

    def configure_lora(self) -> LoraConfig:
        """LoRA: r=16, alpha=32, target q_proj + v_proj."""

    def train(self, dataset: Dataset, output_dir: str, epochs: int = 3):
        """Run SFT with TRL's SFTTrainer."""

    def evaluate(self, test_dataset: Dataset) -> Dict[str, float]:
        """Evaluate on held-out test set."""

    def export_for_serving(self, adapter_path: str, output_path: str):
        """Merge LoRA weights or export adapter for vLLM."""
```

### 2.4 Task-Specific Data Formatters

**Create:** `src/ai/training/data_formatters.py`

**ImagePromptFormatter** -- converts training log to:
```json
{
  "messages": [
    {"role": "system", "content": "You are Nevo's image prompt generator..."},
    {"role": "user", "content": "Concept: photosynthesis\nLearning style: visual\nInterests: animals, nature"},
    {"role": "assistant", "content": "A bright, colorful illustration showing a smiling green leaf..."}
  ]
}
```

**QuizQuestionFormatter** -- converts training log to:
```json
{
  "messages": [
    {"role": "system", "content": "You generate educational quiz questions as JSON..."},
    {"role": "user", "content": "Lesson: Basic Addition...\nReading level: grade_3\nQuestions: 3"},
    {"role": "assistant", "content": "[{\"question\": \"What is 2 + 3?\", ...}]"}
  ]
}
```

### 2.5 Training Configuration

**Create:** `src/ai/training/config.py`

| Parameter | image_prompt | quiz_questions |
|-----------|-------------|----------------|
| base_model | `Qwen/Qwen2.5-3B-Instruct` | `Qwen/Qwen2.5-3B-Instruct` |
| max_seq_length | 512 | 2048 |
| lora_r | 16 | 16 |
| lora_alpha | 32 | 32 |
| target_modules | `["q_proj", "v_proj"]` | `["q_proj", "v_proj"]` |
| epochs | 3 | 3 |
| learning_rate | 2e-4 | 2e-4 |
| batch_size | 4 | 4 |
| min_training_samples | 800 | 1500 |
| test_split_ratio | 0.1 | 0.1 |

### 2.6 Training CLI

**Create:** `src/ai/scripts/train_slm.py`

```bash
# Train image prompt adapter
python -m src.ai.scripts.train_slm --task image_prompt --output models/nevo-slm-image-v1

# Train quiz questions adapter
python -m src.ai.scripts.train_slm --task quiz_questions --output models/nevo-slm-quiz-v1

# Evaluate existing adapter
python -m src.ai.scripts.train_slm --task image_prompt --evaluate-only --adapter models/nevo-slm-image-v1
```

### 2.7 Dependencies

**Create:** `requirements-training.txt` (separate from production)

```
torch>=2.1.0
transformers>=4.40.0
peft>=0.10.0
datasets>=2.18.0
accelerate>=0.28.0
bitsandbytes>=0.43.0
trl>=0.8.0
```

### Files to Create

| Action | File |
|--------|------|
| Create | `src/ai/training/__init__.py` |
| Create | `src/ai/training/fine_tuning_pipeline.py` |
| Create | `src/ai/training/data_formatters.py` |
| Create | `src/ai/training/config.py` |
| Create | `src/ai/scripts/train_slm.py` |
| Create | `requirements-training.txt` |

---

## Phase 3: Deploy SLM for 2 Tasks (Weeks 13-18)

> **Status: NOT STARTED**
> **Depends on:** Phase 2 producing trained adapters with acceptable quality

### 3.1 NevoSLMService

**Create:** `src/infrastructure/external/ai/nevo_slm_service.py`

Calls a local vLLM inference server via OpenAI-compatible API:

```python
class NevoSLMService:
    """Nevo's own Small Language Model service."""

    supported_tasks = {"image_prompt", "quiz_questions"}

    async def generate_image_prompt(self, concept: str, profile: NeuroProfile) -> str:
        messages = self._format_image_prompt_messages(concept, profile)
        response = await self._call_model(messages, adapter="image_prompt")
        return response.strip()

    async def generate_quiz_questions(self, lesson_content: str, profile: NeuroProfile, num_questions: int = 3) -> List[Dict]:
        messages = self._format_quiz_messages(lesson_content, profile, num_questions)
        response = await self._call_model(messages, adapter="quiz_questions")
        return self._parse_and_validate_quiz_json(response)

    async def _call_model(self, messages, adapter: str) -> str:
        """Call vLLM's OpenAI-compatible endpoint."""
        payload = {
            "model": f"nevo-slm-{adapter}",
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.7,
        }
        response = await self.http_client.post(f"{self.base_url}/v1/chat/completions", json=payload)
        return response.json()["choices"][0]["message"]["content"]
```

### 3.2 HybridAIService (The Router)

**Create:** `src/infrastructure/external/ai/hybrid_ai_service.py`

Implements `IAIService` and routes each method to SLM or Gemini:

```
Request Routing:

  generate_image_prompt    -> SLM (fallback to Gemini on error)
  generate_quiz_questions  -> SLM (fallback to Gemini on error or invalid JSON)
  generate_chat_response   -> Gemini (until Phase 5a)
  adapt_lesson             -> Gemini (until Phase 5b)
  generate_student_profile -> Gemini (until Phase 5c)
```

Key features:
- **Automatic fallback:** If SLM fails or returns invalid output, seamlessly falls back to Gemini
- **A/B testing:** Configurable rollout percentage per task (start at 10%, increase to 100%)
- **Output validation:** Quiz JSON schema is validated before accepting SLM output
- **Logging continues:** Both SLM and Gemini responses are logged (with different `model_name`)

### 3.3 Routing Configuration

**Create:** `src/ai/config/routing_config.py`

```python
@dataclass
class RoutingConfig:
    slm_enabled_tasks: Set[str]         # {"image_prompt", "quiz_questions"}
    rollout_percentage: Dict[str, int]  # {"image_prompt": 50, "quiz_questions": 25}
    fallback_enabled: bool = True       # Fall back to Gemini on SLM failure
```

### 3.4 New Settings

```python
# In settings.py
nevo_slm_enabled: bool = False
nevo_slm_url: str = "http://localhost:8080"
nevo_slm_tasks: str = ""           # comma-separated: "image_prompt,quiz_questions"
nevo_slm_rollout_pct: int = 0     # 0-100, percentage of requests to SLM
```

### 3.5 Inference Server Setup

Serve using vLLM with LoRA adapter hot-swapping (one base model, two adapters):

```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-3B-Instruct \
  --enable-lora \
  --lora-modules image_prompt=./adapters/image_prompt quiz_questions=./adapters/quiz_questions \
  --port 8080 \
  --max-model-len 2048
```

Hardware requirements:
- **Minimum:** 8GB VRAM GPU (RTX 3060/4060 or equivalent)
- **Recommended:** 16GB VRAM GPU (RTX 4080 or A10)
- **CPU-only fallback:** Works but ~10x slower (acceptable for non-real-time tasks like image prompts)

### Files to Create/Modify

| Action | File |
|--------|------|
| Create | `src/infrastructure/external/ai/nevo_slm_service.py` |
| Create | `src/infrastructure/external/ai/hybrid_ai_service.py` |
| Create | `src/ai/config/routing_config.py` |
| Create | `src/ai/serving/docker-compose.slm.yml` |
| Create | `src/ai/serving/serve_config.yaml` |
| Modify | `src/presentation/api/v1/dependencies/services.py` |
| Modify | `src/core/config/settings.py` |

---

## Phase 4: Quality Assurance & Evaluation (Weeks 16-22)

> **Status: NOT STARTED**
> **Depends on:** Phase 3 serving some percentage of traffic through SLM

### 4.1 Evaluation Framework

**Create:** `src/ai/evaluation/evaluator.py`

**Image Prompt Metrics:**

| Metric | Target | How Measured |
|--------|--------|-------------|
| Non-empty output | > 99% | `len(output) > 0` |
| Length ratio vs Gemini | 80-120% | Compare avg lengths |
| Concept keyword presence | > 90% | Input concept words found in output |
| Student interest reference | > 70% | Profile interests mentioned |

**Quiz Question Metrics:**

| Metric | Target | How Measured |
|--------|--------|-------------|
| Valid JSON | > 97% | `json.loads()` succeeds |
| Schema compliance | > 95% | All required fields present with correct types |
| Correct question count | > 95% | `len(questions) == num_questions` |
| `correct_index` valid | > 99% | `0 <= correct_index < len(options)` |
| Lesson relevance | > 80% | Keyword overlap between lesson and questions |

### 4.2 A/B Test Analyzer

**Create:** `src/ai/evaluation/ab_test_analyzer.py`

Since `LoggingAIService` records `model_name` for every interaction, we can compare:

```
SLM outputs (model_name = "nevo-slm")  vs  Gemini outputs (model_name = "gemini-2.5-flash")

Compare:
- Success rate (no errors/fallbacks)
- Output quality metrics (above)
- Student engagement (for adapted lessons: view_count, completion_count, time_spent)
- Statistical significance (chi-squared test for proportions)
```

### 4.3 Quality Gates for Rollout Progression

| Rollout Stage | image_prompt Gate | quiz_questions Gate |
|---------------|-------------------|---------------------|
| 0% -> 10% | Model trained, basic tests pass | Model trained, JSON validity > 90% |
| 10% -> 50% | Error rate < 2%, 200+ A/B samples | Error rate < 3%, schema compliance > 93% |
| 50% -> 100% | Error rate < 1%, quality within 90% of Gemini | Error rate < 2%, schema compliance > 97% |

### 4.4 Monitoring Dashboard

**Extend:** `src/presentation/api/v1/endpoints/admin.py`

```
GET /api/v1/admin/slm/metrics                 -> real-time quality metrics per task
GET /api/v1/admin/slm/ab-test/{task_type}     -> A/B test comparison results
PATCH /api/v1/admin/slm/rollout/{task_type}   -> adjust rollout percentage
```

---

## Phase 5: Expansion Roadmap (Months 8-24)

> **Status: NOT STARTED**
> **Depends on:** Phases 1-4 proven successful for 2 initial tasks

### Phase 5a: `generate_chat_response` (Months 8-12)

| Aspect | Detail |
|--------|--------|
| **Model** | Upgrade to Qwen 2.5-7B or Llama 3.2-8B |
| **Training data** | `chat_messages` table -- every student/Nevo exchange |
| **Format** | Multi-turn conversation fine-tuning (system + chat history + new response) |
| **Challenge** | Personality consistency, context tracking, open-ended output |
| **Evaluation** | BLEU/ROUGE against Gemini baseline + human teacher review |
| **Min samples** | ~3,000 conversation turns |

### Phase 5b: `adapt_lesson` (Months 12-18)

| Aspect | Detail |
|--------|--------|
| **Model** | Same 7B model, dedicated LoRA adapter |
| **Training data** | `adapted_lessons.content_blocks` as ground truth outputs |
| **Format** | Input: lesson title + content + 6 profile attributes. Output: full blocks JSON |
| **Challenge** | Complex multi-block JSON, 6 student attributes to balance, content coherence |
| **Evaluation** | JSON validity + block count + human review from teachers |
| **Strategy** | May need two-stage: structure planning then content filling |
| **DPO data** | Teacher corrections via `human_correction` field in training logs |
| **Min samples** | ~2,000 adapted lessons |

### Phase 5c: `generate_student_profile` (Months 18-24)

| Aspect | Detail |
|--------|--------|
| **Model** | Same 7B model, dedicated LoRA adapter |
| **Training data** | `neuro_profiles.assessment_raw_data` -> `generated_profile` pairs |
| **Format** | Assessment Q&A -> structured profile JSON |
| **Challenge** | Highest stakes -- wrong profile = wrong personalization for entire student journey |
| **Evaluation** | Domain expert review (not just automated metrics) |
| **Strategy** | Keep Gemini as "second opinion" -- both generate profiles, flag discrepancies |
| **Min samples** | ~1,000 profiles (with teacher validation data) |

---

## Architecture Diagrams

### Current Architecture (Gemini Only)

```
Student Request
      |
      v
  FastAPI Endpoint
      |
      v
  get_ai_service()  -->  GeminiAIService  -->  Google Gemini API
      |                                              |
      v                                              v
  Response to Student                          (no data captured)
```

### Phase 1 Architecture (+ Data Collection)

```
Student Request
      |
      v
  FastAPI Endpoint
      |
      v
  get_ai_service()  -->  LoggingAIService  -->  GeminiAIService  -->  Google Gemini API
                              |                                            |
                              v                                            v
                    training_data_logs  <--- logs input_context + model_output
                         (PostgreSQL)
```

### Phase 3+ Architecture (Hybrid SLM + Gemini)

```
Student Request
      |
      v
  FastAPI Endpoint
      |
      v
  get_ai_service()  -->  LoggingAIService  -->  HybridAIService
                              |                       |
                              v                       +-- image_prompt ----> NevoSLMService ---> vLLM (local)
                    training_data_logs                |                           |
                                                      +-- quiz_questions --> NevoSLMService ---> vLLM (local)
                                                      |                           |
                                                      +-- chat_response ---> GeminiAIService --> Google API
                                                      +-- adapt_lesson ----> GeminiAIService --> Google API
                                                      +-- student_profile -> GeminiAIService --> Google API
                                                      |
                                                      +-- (fallback on SLM error) -> GeminiAIService
```

### Final Architecture (Full SLM, Month 24)

```
Student Request
      |
      v
  FastAPI Endpoint
      |
      v
  get_ai_service()  -->  LoggingAIService  -->  NevoSLMService  -->  vLLM (self-hosted)
                              |                                          |
                              v                                    Qwen 7B + 5 LoRA adapters
                    training_data_logs                             (one per task)
                    (continuous learning)
                                                              Gemini kept as optional fallback
```

---

## Timeline Summary

```
Month:  1    2    3    4    5    6    7    8    9    10   11   12   ...  18   ...  24
        |----|----|----|----|----|----|----|----|----|----|----|----|    |----|    |----|

Phase 1: [====DATA COLLECTION (ongoing)==================================================>]
Phase 2:           [====TRAINING PIPELINE====]
Phase 3:                     [====DEPLOY 2 TASKS====]
Phase 4:                          [====EVALUATION====]
Phase 5a:                                        [====CHAT========]
Phase 5b:                                                          [====ADAPT====]
Phase 5c:                                                                    [====PROFILE====]

Gemini Usage:  100% ------------------------------------------> ~60% ------> ~20% -----> ~0%
SLM Usage:     0%   ------------------------------------------> ~40% ------> ~80% -----> ~100%
```

| Phase | Timeline | Gemini Reduction | What's on SLM |
|-------|----------|-----------------|---------------|
| Phase 1 | Weeks 1-4 | 0% (data collection only) | Nothing yet |
| Phase 2 | Weeks 5-12 | 0% (training pipeline) | Nothing yet |
| Phase 3 | Weeks 13-18 | ~20% (2 tasks moved) | image_prompt, quiz_questions |
| Phase 4 | Weeks 16-22 | ~20% (quality verified) | image_prompt, quiz_questions |
| Phase 5a | Months 8-12 | ~40% | + chat_response |
| Phase 5b | Months 12-18 | ~70% | + adapt_lesson |
| Phase 5c | Months 18-24 | ~95-100% | + student_profile |

---

## Hardware Requirements

### Training (Phase 2)

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | 1x RTX 3060 (12GB) | 1x RTX 4090 (24GB) or A100 (40GB) |
| RAM | 16GB | 32GB |
| Storage | 50GB SSD | 200GB NVMe |
| Training time (3B, 1K samples) | ~4 hours | ~1 hour |

### Inference (Phase 3+)

| Component | 3B Model (Tasks 1-2) | 7B Model (Tasks 3-5) |
|-----------|---------------------|----------------------|
| GPU | 1x RTX 3060 (12GB) or CPU | 1x RTX 4080 (16GB) |
| RAM | 8GB | 16GB |
| Latency (GPU) | ~1-3 seconds | ~2-5 seconds |
| Latency (CPU) | ~10-30 seconds | ~30-60 seconds |
| Cost vs Gemini | ~$50/month server vs $200+/month API | ~$100/month server vs $400+/month API |

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| SLM quality is poor | Gemini fallback is always available; rollout is gradual (10% -> 50% -> 100%) |
| Not enough training data | Phase 1 starts immediately; synthetic data augmentation possible |
| Model too slow for chat | Chat stays on Gemini longer; optimize with quantization (INT4/INT8) |
| JSON output unreliable | Strict schema validation; fallback to Gemini on parse failure |
| Hardware costs too high | Start with CPU inference for non-real-time tasks; GPU only for chat |
| Model drift over time | Continuous data collection + periodic retraining (monthly) |
| Student profile accuracy | Keep Gemini as dual-check for profiles; human expert review |

---

## Success Metrics

| Metric | Phase 3 Target | Phase 5 Target |
|--------|---------------|----------------|
| Gemini API cost reduction | 20% | 95%+ |
| SLM inference latency | < 5s for tasks 1-2 | < 10s for all tasks |
| SLM quality vs Gemini | Within 90% | Within 95% |
| Fallback rate | < 5% | < 2% |
| Student engagement (A/B) | No significant difference | Parity or better |
| Self-hosted uptime | 99% | 99.5% |
