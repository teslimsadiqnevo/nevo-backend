-- Initial Schema Migration
-- Nevo AI-Powered Personalized Learning Platform
-- Tables: schools, training_data_logs, users, neuro_profiles,
--         assessments, lessons, student_progress, adapted_lessons

-- ============================================================
-- EXTENSIONS
-- ============================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- ENUM TYPES
-- ============================================================
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM (
        'student', 'teacher', 'school_admin', 'parent', 'super_admin'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE learning_style AS ENUM (
        'visual', 'auditory', 'kinesthetic', 'reading_writing', 'multimodal'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE reading_level AS ENUM (
        'pre_k', 'grade_1', 'grade_2', 'grade_3', 'grade_4',
        'grade_5', 'grade_6', 'grade_7', 'grade_8', 'high_school'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE complexity_tolerance AS ENUM ('low', 'medium', 'high');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE assessment_status AS ENUM (
        'not_started', 'in_progress', 'completed', 'processing'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE lesson_status AS ENUM ('draft', 'published', 'archived');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE adapted_lesson_status AS ENUM (
        'pending', 'generating', 'ready', 'failed'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ============================================================
-- TABLES (dependency order)
-- ============================================================

-- 1. schools (no dependencies)
CREATE TABLE IF NOT EXISTS schools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) NOT NULL DEFAULT 'Nigeria',
    postal_code VARCHAR(20),
    phone_number VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(500),
    logo_url VARCHAR(2048),
    is_active BOOLEAN NOT NULL DEFAULT true,
    subscription_tier VARCHAR(50) NOT NULL DEFAULT 'free',
    max_teachers INTEGER NOT NULL DEFAULT 5,
    max_students INTEGER NOT NULL DEFAULT 100,
    teacher_count INTEGER NOT NULL DEFAULT 0,
    student_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. training_data_logs (no foreign keys to app tables)
CREATE TABLE IF NOT EXISTS training_data_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    input_context JSONB NOT NULL DEFAULT '{}',
    model_output JSONB NOT NULL DEFAULT '{}',
    human_correction JSONB,
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    prompt_template_version VARCHAR(50),
    metric_score DOUBLE PRECISION,
    quality_rating INTEGER,
    was_accepted BOOLEAN NOT NULL DEFAULT true,
    corrected_by_user_id UUID,
    correction_type VARCHAR(50),
    correction_notes VARCHAR(1000),
    is_processed BOOLEAN NOT NULL DEFAULT false,
    processed_at TIMESTAMPTZ,
    training_batch_id VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_training_data_logs_source_id ON training_data_logs(source_id);
CREATE INDEX IF NOT EXISTS idx_training_data_logs_source_type ON training_data_logs(source_type);
CREATE INDEX IF NOT EXISTS idx_training_data_logs_is_processed ON training_data_logs(is_processed);
CREATE INDEX IF NOT EXISTS idx_training_data_logs_training_batch_id ON training_data_logs(training_batch_id);

-- 3. users (references schools)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    age INTEGER,
    school_id UUID REFERENCES schools(id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_verified BOOLEAN NOT NULL DEFAULT false,
    avatar_url VARCHAR(2048),
    phone_number VARCHAR(20),
    last_login_at TIMESTAMPTZ,
    linked_student_ids UUID[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_school_id ON users(school_id);

-- 4. neuro_profiles (references users)
CREATE TABLE IF NOT EXISTS neuro_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    assessment_raw_data JSONB NOT NULL DEFAULT '{}',
    learning_style learning_style NOT NULL DEFAULT 'visual',
    reading_level reading_level NOT NULL DEFAULT 'grade_3',
    complexity_tolerance complexity_tolerance NOT NULL DEFAULT 'medium',
    attention_span_minutes INTEGER NOT NULL DEFAULT 15,
    sensory_triggers JSONB NOT NULL DEFAULT '[]',
    interests TEXT[],
    preferred_subjects TEXT[],
    generated_profile JSONB NOT NULL DEFAULT '{}',
    confidence_scores JSONB NOT NULL DEFAULT '{}',
    last_updated TIMESTAMPTZ,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_neuro_profiles_user_id ON neuro_profiles(user_id);

-- 5. assessments (references users)
CREATE TABLE IF NOT EXISTS assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    status assessment_status NOT NULL DEFAULT 'not_started',
    answers JSONB NOT NULL DEFAULT '[]',
    current_question_index INTEGER NOT NULL DEFAULT 0,
    total_questions INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    generated_profile_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_assessments_student_id ON assessments(student_id);
CREATE INDEX IF NOT EXISTS idx_assessments_status ON assessments(status);

-- 6. lessons (references users, schools)
CREATE TABLE IF NOT EXISTS lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    teacher_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    school_id UUID REFERENCES schools(id) ON DELETE SET NULL,
    description TEXT,
    original_text_content TEXT NOT NULL,
    media_url VARCHAR(2048),
    media_type VARCHAR(50),
    subject VARCHAR(100),
    topic VARCHAR(255),
    target_grade_level INTEGER NOT NULL DEFAULT 3,
    estimated_duration_minutes INTEGER NOT NULL DEFAULT 30,
    tags TEXT[],
    status lesson_status NOT NULL DEFAULT 'draft',
    published_at TIMESTAMPTZ,
    view_count INTEGER NOT NULL DEFAULT 0,
    adaptation_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_lessons_teacher_id ON lessons(teacher_id);
CREATE INDEX IF NOT EXISTS idx_lessons_school_id ON lessons(school_id);
CREATE INDEX IF NOT EXISTS idx_lessons_status ON lessons(status);
CREATE INDEX IF NOT EXISTS idx_lessons_subject ON lessons(subject);

-- 7. student_progress (references users)
CREATE TABLE IF NOT EXISTS student_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    lesson_progress JSONB NOT NULL DEFAULT '{}',
    skill_progress JSONB NOT NULL DEFAULT '{}',
    total_lessons_completed INTEGER NOT NULL DEFAULT 0,
    total_time_spent_seconds INTEGER NOT NULL DEFAULT 0,
    average_score DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    current_streak_days INTEGER NOT NULL DEFAULT 0,
    longest_streak_days INTEGER NOT NULL DEFAULT 0,
    last_activity_at TIMESTAMPTZ,
    last_lesson_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_student_progress_student_id ON student_progress(student_id);

-- 8. adapted_lessons (references lessons, users)
CREATE TABLE IF NOT EXISTS adapted_lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_title VARCHAR(255) NOT NULL,
    adaptation_style VARCHAR(255),
    content_blocks JSONB NOT NULL DEFAULT '[]',
    status adapted_lesson_status NOT NULL DEFAULT 'pending',
    is_active BOOLEAN NOT NULL DEFAULT true,
    ai_model_used VARCHAR(100),
    generation_prompt_hash VARCHAR(64),
    generation_duration_ms INTEGER,
    view_count INTEGER NOT NULL DEFAULT 0,
    completion_count INTEGER NOT NULL DEFAULT 0,
    average_time_spent_seconds INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_adapted_lesson_student UNIQUE (lesson_id, student_id)
);

CREATE INDEX IF NOT EXISTS idx_adapted_lessons_lesson_id ON adapted_lessons(lesson_id);
CREATE INDEX IF NOT EXISTS idx_adapted_lessons_student_id ON adapted_lessons(student_id);
CREATE INDEX IF NOT EXISTS idx_adapted_lessons_status ON adapted_lessons(status);

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================
ALTER TABLE schools ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE neuro_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE lessons ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE adapted_lessons ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_data_logs ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- AUTO-UPDATE updated_at TRIGGER
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_schools_updated_at BEFORE UPDATE ON schools
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_neuro_profiles_updated_at BEFORE UPDATE ON neuro_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_assessments_updated_at BEFORE UPDATE ON assessments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lessons_updated_at BEFORE UPDATE ON lessons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_student_progress_updated_at BEFORE UPDATE ON student_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_adapted_lessons_updated_at BEFORE UPDATE ON adapted_lessons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_training_data_logs_updated_at BEFORE UPDATE ON training_data_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
