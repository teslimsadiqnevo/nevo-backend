-- Seed data for Nevo development/staging
-- All users have password: password123
-- bcrypt hash: $2b$12$VaDH.FbatD77RhfaYu3agOFHcwEZ3jVh2sdidhk8N9I4IQU.J17qS

-- ============================================================
-- 1. School
-- ============================================================
INSERT INTO schools (id, name, address, city, state, country, is_active, subscription_tier, max_teachers, max_students, teacher_count, student_count, created_at, updated_at)
VALUES (
    'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d',
    'Greenfield Academy',
    '12 Admiralty Way, Lekki Phase 1',
    'Lagos',
    'Lagos',
    'Nigeria',
    true,
    'premium',
    10,
    200,
    1,
    1,
    now(),
    now()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 2. School Admin
-- ============================================================
INSERT INTO users (id, email, password_hash, role, first_name, last_name, school_id, is_active, is_verified, created_at, updated_at)
VALUES (
    'b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e',
    'admin@greenfield.edu.ng',
    '$2b$12$VaDH.FbatD77RhfaYu3agOFHcwEZ3jVh2sdidhk8N9I4IQU.J17qS',
    'SCHOOL_ADMIN',
    'Adaobi',
    'Okafor',
    'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d',
    true,
    true,
    now(),
    now()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 3. Teacher
-- ============================================================
INSERT INTO users (id, email, password_hash, role, first_name, last_name, school_id, is_active, is_verified, created_at, updated_at)
VALUES (
    'c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f',
    'adewale@greenfield.edu.ng',
    '$2b$12$VaDH.FbatD77RhfaYu3agOFHcwEZ3jVh2sdidhk8N9I4IQU.J17qS',
    'TEACHER',
    'Adewale',
    'Johnson',
    'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d',
    true,
    true,
    now(),
    now()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 4. Student
-- ============================================================
INSERT INTO users (id, email, password_hash, role, first_name, last_name, age, school_id, is_active, is_verified, nevo_id, created_at, updated_at)
VALUES (
    'd4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f80',
    'lydia@greenfield.edu.ng',
    '$2b$12$VaDH.FbatD77RhfaYu3agOFHcwEZ3jVh2sdidhk8N9I4IQU.J17qS',
    'STUDENT',
    'Lydia',
    'Adeyemi',
    10,
    'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d',
    true,
    true,
    'NEVO-LYDIA',
    now(),
    now()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 5. Parent (linked to student Lydia)
-- ============================================================
INSERT INTO users (id, email, password_hash, role, first_name, last_name, is_active, is_verified, linked_student_ids, created_at, updated_at)
VALUES (
    'e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8091',
    'mrs.adeyemi@gmail.com',
    '$2b$12$VaDH.FbatD77RhfaYu3agOFHcwEZ3jVh2sdidhk8N9I4IQU.J17qS',
    'PARENT',
    'Funke',
    'Adeyemi',
    true,
    true,
    ARRAY['d4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f80']::uuid[],
    now(),
    now()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 6. NeuroProfile for student Lydia
-- ============================================================
INSERT INTO neuro_profiles (id, user_id, learning_style, reading_level, complexity_tolerance, attention_span_minutes, sensory_triggers, interests, preferred_subjects, assessment_raw_data, generated_profile, confidence_scores, version, created_at, updated_at)
VALUES (
    'f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f809102',
    'd4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f80',
    'VISUAL',
    'GRADE_3',
    'MEDIUM',
    15,
    '["loud_sounds"]',
    ARRAY['science', 'art', 'music'],
    ARRAY['mathematics', 'science'],
    '{}',
    '{"learning_preference": "visual", "complexity_tolerance": "medium"}',
    '{}',
    1,
    now(),
    now()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 7. Sample lesson by teacher
-- ============================================================
INSERT INTO lessons (id, title, teacher_id, school_id, description, original_text_content, subject, topic, target_grade_level, estimated_duration_minutes, status, view_count, adaptation_count, created_at, updated_at)
VALUES (
    'a7b8c9d0-e1f2-4a3b-4c5d-6e7f80910213',
    'Introduction to Fractions',
    'c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f',
    'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d',
    'Learn what fractions are and how to use them in everyday life.',
    'A fraction represents a part of a whole. When we divide something into equal parts, each part is a fraction. For example, if you cut a pizza into 4 equal slices and eat 1 slice, you have eaten 1/4 (one quarter) of the pizza. The top number (numerator) tells us how many parts we have. The bottom number (denominator) tells us how many equal parts the whole is divided into. Fractions are everywhere: half a cup of water is 1/2, a quarter of an hour is 15 minutes, and sharing 3 apples equally among 4 friends means each person gets 3/4 of an apple.',
    'Mathematics',
    'Fractions',
    3,
    30,
    'PUBLISHED',
    0,
    0,
    now(),
    now()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 8. Student progress (Lydia started the fractions lesson)
-- ============================================================
INSERT INTO student_progress (id, student_id, total_lessons_completed, total_time_spent_seconds, average_score, current_streak_days, longest_streak_days, last_lesson_id, lesson_progress, skill_progress, last_activity_at, created_at, updated_at)
VALUES (
    'b8c9d0e1-f2a3-4b4c-5d6e-7f8091021324',
    'd4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f80',
    0,
    300,
    0.0,
    1,
    1,
    'a7b8c9d0-e1f2-4a3b-4c5d-6e7f80910213',
    '{"a7b8c9d0-e1f2-4a3b-4c5d-6e7f80910213": {"lesson_id": "a7b8c9d0-e1f2-4a3b-4c5d-6e7f80910213", "status": "in_progress", "blocks_completed": 2, "total_blocks": 5, "time_spent_seconds": 300, "score": null}}',
    '{}',
    now(),
    now(),
    now()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 9. Teacher feedback to Lydia
-- ============================================================
INSERT INTO teacher_feedbacks (id, teacher_id, student_id, lesson_id, message, created_at, updated_at)
VALUES (
    'c9d0e1f2-a3b4-4c5d-6e7f-809102132435',
    'c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f',
    'd4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f80',
    'a7b8c9d0-e1f2-4a3b-4c5d-6e7f80910213',
    'Great start on fractions, Lydia! Keep going, you are doing amazing!',
    now(),
    now()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- Summary of seed accounts
-- ============================================================
-- | Role         | Email                        | Password    |
-- |------------- |------------------------------|-------------|
-- | school_admin | admin@greenfield.edu.ng      | password123 |
-- | teacher      | adewale@greenfield.edu.ng    | password123 |
-- | student      | lydia@greenfield.edu.ng      | password123 |
-- | parent       | mrs.adeyemi@gmail.com        | password123 |
