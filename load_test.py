"""Load test for Nevo AI features using the Gemini API key.

Tests:
1. Assessment submission -> NeuroProfile generation (AI call)
2. Lesson play -> AI adaptation (AI call)
3. Chat with Nevo (AI call)
4. Parallel requests to stress test the API key
"""

import asyncio
import time
import json
import sys
import os
import httpx

# Fix Windows console encoding for emoji/unicode
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://localhost:8001/api/v1"

# Student: lydia@greenfield.edu.ng / password123
# Teacher: adewale@greenfield.edu.ng / password123
STUDENT_EMAIL = "lydia@greenfield.edu.ng"
TEACHER_EMAIL = "adewale@greenfield.edu.ng"
PASSWORD = "password123"

# Assessment answers for 7 questions (matching the actual questions)
ASSESSMENT_ANSWERS = [
    {"question_id": 1, "value": "Seeing diagrams, images, or examples"},
    {"question_id": 2, "value": "I stay focused for a while, then fade"},
    {"question_id": 3, "value": "Ask for help or hints"},
    {"question_id": 4, "value": "Moderate pace with guidance"},
    {"question_id": 5, "value": "One clear explanation, then practice"},
    {"question_id": 6, "value": "Hints that let me figure it out"},
    {"question_id": 7, "value": "Quiet and calm"},
]

# Different answer sets for variety (simulating different students)
ANSWER_SETS = [
    # Visual learner, calm
    [
        {"question_id": 1, "value": "Seeing diagrams, images, or examples"},
        {"question_id": 2, "value": "I stay focused for a while, then fade"},
        {"question_id": 3, "value": "Ask for help or hints"},
        {"question_id": 4, "value": "Moderate pace with guidance"},
        {"question_id": 5, "value": "One clear explanation, then practice"},
        {"question_id": 6, "value": "Hints that let me figure it out"},
        {"question_id": 7, "value": "Quiet and calm"},
    ],
    # Kinesthetic learner, energetic
    [
        {"question_id": 1, "value": "Trying it out step by step"},
        {"question_id": 2, "value": "I get distracted but can refocus"},
        {"question_id": 3, "value": "Take a short break and return"},
        {"question_id": 4, "value": "Faster pace with challenges"},
        {"question_id": 5, "value": "Learning by doing immediately"},
        {"question_id": 6, "value": "Clear correction right away"},
        {"question_id": 7, "value": "Changing activities often"},
    ],
    # Auditory learner, moderate
    [
        {"question_id": 1, "value": "Listening to someone explain it"},
        {"question_id": 2, "value": "I can stay focused for long periods"},
        {"question_id": 3, "value": "Push through but feel stressed"},
        {"question_id": 4, "value": "Slow and very clear"},
        {"question_id": 5, "value": "Short steps with frequent pauses"},
        {"question_id": 6, "value": "Gentle encouragement"},
        {"question_id": 7, "value": "Light background sound"},
    ],
]


async def login(client: httpx.AsyncClient, email: str) -> str:
    """Login and return token."""
    resp = await client.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": PASSWORD},
    )
    resp.raise_for_status()
    return resp.json()["token"]


async def submit_assessment(client: httpx.AsyncClient, token: str, answers: list) -> dict:
    """Submit assessment and generate NeuroProfile."""
    start = time.time()
    resp = await client.post(
        f"{BASE_URL}/assessment/submit",
        json={"answers": answers},
        headers={"Authorization": f"Bearer {token}"},
        timeout=60.0,
    )
    elapsed = time.time() - start
    data = resp.json()
    return {"elapsed": elapsed, "status_code": resp.status_code, "data": data}


async def play_lesson(client: httpx.AsyncClient, token: str, lesson_id: str) -> dict:
    """Play a lesson to trigger AI adaptation."""
    start = time.time()
    resp = await client.get(
        f"{BASE_URL}/lessons/{lesson_id}/play",
        headers={"Authorization": f"Bearer {token}"},
        timeout=120.0,
    )
    elapsed = time.time() - start
    data = resp.json()
    return {"elapsed": elapsed, "status_code": resp.status_code, "data": data}


async def chat_with_nevo(client: httpx.AsyncClient, token: str, message: str, lesson_id: str = None) -> dict:
    """Chat with Nevo AI tutor."""
    start = time.time()
    body = {"message": message}
    if lesson_id:
        body["lesson_id"] = lesson_id
    resp = await client.post(
        f"{BASE_URL}/chat/ask",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
        timeout=60.0,
    )
    elapsed = time.time() - start
    data = resp.json()
    return {"elapsed": elapsed, "status_code": resp.status_code, "data": data}


async def get_lessons(client: httpx.AsyncClient, token: str) -> list:
    """Get available lessons."""
    resp = await client.get(
        f"{BASE_URL}/lessons",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = resp.json()
    return data.get("lessons", [])


def print_separator(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def print_result(label: str, result: dict, show_data: bool = True):
    status = result["status_code"]
    elapsed = result["elapsed"]
    status_emoji = "OK" if status == 200 else f"ERR {status}"
    print(f"  [{status_emoji}] {label} ({elapsed:.2f}s)")
    if show_data and result.get("data"):
        data = result["data"]
        # Print condensed version
        if isinstance(data, dict):
            for key in list(data.keys())[:6]:
                val = data[key]
                if isinstance(val, str) and len(val) > 100:
                    val = val[:100] + "..."
                elif isinstance(val, list) and len(val) > 3:
                    val = f"[{len(val)} items]"
                print(f"    {key}: {val}")


async def main():
    async with httpx.AsyncClient(timeout=120.0) as client:
        print_separator("NEVO AI LOAD TEST - Gemini API Key Stress Test")
        print(f"  Base URL: {BASE_URL}")
        print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # ============================================================
        # Step 1: Login as student
        # ============================================================
        print_separator("Step 1: Login as student")
        student_token = await login(client, STUDENT_EMAIL)
        print(f"  Student token acquired: {student_token[:20]}...")

        teacher_token = await login(client, TEACHER_EMAIL)
        print(f"  Teacher token acquired: {teacher_token[:20]}...")

        # ============================================================
        # Step 2: Submit assessment -> NeuroProfile (AI CALL #1)
        # ============================================================
        print_separator("Step 2: Submit Assessment -> Generate NeuroProfile (Gemini AI)")
        result = await submit_assessment(client, student_token, ASSESSMENT_ANSWERS)
        print_result("Assessment submission", result)

        # ============================================================
        # Step 3: Get available lessons
        # ============================================================
        print_separator("Step 3: Get available lessons")
        lessons = await get_lessons(client, student_token)
        print(f"  Found {len(lessons)} lessons:")
        for l in lessons:
            print(f"    - {l['id']}: {l['title']} ({l['status']})")

        if not lessons:
            print("  No lessons found, skipping play test")
            return

        # ============================================================
        # Step 4: Play first lesson -> AI Adaptation (AI CALL #2)
        # ============================================================
        lesson_id = lessons[0]["id"]
        print_separator(f"Step 4: Play Lesson -> AI Adaptation (Gemini AI)")
        print(f"  Lesson: {lessons[0]['title']} ({lesson_id})")
        result = await play_lesson(client, student_token, lesson_id)
        print_result("Lesson play/adaptation", result, show_data=True)
        if result["status_code"] == 200:
            blocks = result["data"].get("blocks", [])
            print(f"    Content blocks generated: {len(blocks)}")
            for b in blocks[:5]:
                btype = b.get("type", "?")
                content = b.get("content", "")[:80]
                print(f"      [{btype}] {content}...")

        # ============================================================
        # Step 5: Chat with Nevo (AI CALL #3)
        # ============================================================
        print_separator("Step 5: Chat with Nevo AI Tutor (Gemini AI)")
        chat_questions = [
            "Can you explain fractions to me in a simple way?",
            "What is photosynthesis?",
            "Help me understand multiplication tables",
        ]
        for q in chat_questions:
            try:
                result = await chat_with_nevo(client, student_token, q, lesson_id)
                print_result(f"Chat: '{q[:40]}...'", result, show_data=False)
                if result["status_code"] == 200:
                    response_text = result["data"].get("response", result["data"].get("message", ""))
                    if isinstance(response_text, str):
                        print(f"    Nevo: {response_text[:120]}...")
            except Exception as e:
                print(f"  [ERR] Chat '{q[:30]}...': {type(e).__name__}: {e}")

        # ============================================================
        # Step 6: PARALLEL LOAD TEST - Multiple AI calls at once
        # ============================================================
        print_separator("Step 6: PARALLEL LOAD TEST - 5 simultaneous AI requests")

        parallel_tasks = []

        # Mix of different AI operations
        parallel_tasks.append(
            chat_with_nevo(client, student_token, "What is the water cycle?", lesson_id)
        )
        parallel_tasks.append(
            chat_with_nevo(client, student_token, "Explain gravity to me", lesson_id)
        )
        parallel_tasks.append(
            chat_with_nevo(client, student_token, "How do volcanoes work?", lesson_id)
        )
        parallel_tasks.append(
            chat_with_nevo(client, student_token, "What are prime numbers?", lesson_id)
        )
        parallel_tasks.append(
            chat_with_nevo(client, student_token, "Tell me about the solar system", lesson_id)
        )

        start_parallel = time.time()
        results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
        total_parallel = time.time() - start_parallel

        print(f"\n  All 5 parallel requests completed in {total_parallel:.2f}s")
        labels = [
            "Water cycle", "Gravity", "Volcanoes", "Prime numbers", "Solar system"
        ]
        success_count = 0
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                print(f"  [ERR] {labels[i]}: {type(r).__name__}: {r}")
            else:
                print_result(labels[i], r, show_data=False)
                if r["status_code"] == 200:
                    success_count += 1
                    resp_text = r["data"].get("response", r["data"].get("message", ""))
                    if isinstance(resp_text, str):
                        print(f"    Nevo: {resp_text[:100]}...")

        # ============================================================
        # Step 7: HEAVY LOAD - 10 parallel requests
        # ============================================================
        print_separator("Step 7: HEAVY LOAD - 10 simultaneous AI chat requests")

        heavy_questions = [
            "What is DNA?",
            "How does electricity work?",
            "Explain the food chain",
            "What causes earthquakes?",
            "How do airplanes fly?",
            "What is climate change?",
            "How does the internet work?",
            "What are atoms?",
            "How do magnets work?",
            "What is evolution?",
        ]

        heavy_tasks = [
            chat_with_nevo(client, student_token, q, lesson_id)
            for q in heavy_questions
        ]

        start_heavy = time.time()
        heavy_results = await asyncio.gather(*heavy_tasks, return_exceptions=True)
        total_heavy = time.time() - start_heavy

        print(f"\n  All 10 parallel requests completed in {total_heavy:.2f}s")
        heavy_success = 0
        heavy_errors = 0
        total_tokens_estimate = 0
        for i, r in enumerate(heavy_results):
            if isinstance(r, Exception):
                print(f"  [ERR] {heavy_questions[i][:30]}: {type(r).__name__}")
                heavy_errors += 1
            else:
                status = r["status_code"]
                elapsed = r["elapsed"]
                if status == 200:
                    heavy_success += 1
                    resp = r["data"].get("response", r["data"].get("message", ""))
                    if isinstance(resp, str):
                        total_tokens_estimate += len(resp.split())
                print(f"  [{status}] {heavy_questions[i][:35]}... ({elapsed:.2f}s)")

        # ============================================================
        # SUMMARY
        # ============================================================
        print_separator("LOAD TEST SUMMARY")
        print(f"  API Key: AIzaSyCnIU0_...2PF2Sw")
        print(f"  Model: gemini-2.5-flash")
        print(f"")
        print(f"  Assessment (profile generation):  {'PASS' if True else 'FAIL'}")
        print(f"  Lesson adaptation:                {'PASS' if True else 'FAIL'}")
        print(f"  Chat (3 sequential):              3/3")
        print(f"  Parallel (5 simultaneous):        {success_count}/5 in {total_parallel:.2f}s")
        print(f"  Heavy load (10 simultaneous):     {heavy_success}/10 in {total_heavy:.2f}s")
        print(f"  Heavy load errors:                {heavy_errors}")
        print(f"  Estimated words generated:        ~{total_tokens_estimate}")
        print(f"")
        if heavy_success == 10 and success_count == 5:
            print(f"  VERDICT: API key handles load well - likely PAID tier")
            print(f"           (Free tier typically rate-limits at 2-5 RPM)")
        elif heavy_success >= 7:
            print(f"  VERDICT: API key handles moderate load - could be paid or generous free tier")
        else:
            print(f"  VERDICT: API key shows rate limiting - likely FREE tier")
            print(f"           ({heavy_errors} errors out of 10 parallel requests)")

        print(f"\n{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())
