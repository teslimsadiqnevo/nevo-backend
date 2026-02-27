-- Add lesson_assignments table for tracking lesson assignments to students
-- Teachers can assign lessons to their entire class or individual students

-- Create enum types for assignment
DO $$ BEGIN
    CREATE TYPE assignment_status AS ENUM ('ASSIGNED', 'IN_PROGRESS', 'COMPLETED');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE assignment_target AS ENUM ('CLASS', 'INDIVIDUAL');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Create the lesson_assignments table
CREATE TABLE IF NOT EXISTS lesson_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    teacher_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assignment_type assignment_target NOT NULL DEFAULT 'CLASS',
    status assignment_status NOT NULL DEFAULT 'ASSIGNED',
    assigned_at TIMESTAMP NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- A student can only be assigned a lesson once
    CONSTRAINT uq_lesson_student UNIQUE (lesson_id, student_id)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_lesson_assignments_teacher ON lesson_assignments(teacher_id);
CREATE INDEX IF NOT EXISTS idx_lesson_assignments_student ON lesson_assignments(student_id);
CREATE INDEX IF NOT EXISTS idx_lesson_assignments_lesson ON lesson_assignments(lesson_id);
CREATE INDEX IF NOT EXISTS idx_lesson_assignments_status ON lesson_assignments(status);
