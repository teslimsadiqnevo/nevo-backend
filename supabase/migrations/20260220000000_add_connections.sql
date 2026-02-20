-- Add class_code to users table (for teachers)
ALTER TABLE users ADD COLUMN IF NOT EXISTS class_code VARCHAR(20) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_users_class_code ON users(class_code);

-- Create ConnectionStatus enum
DO $$ BEGIN
    CREATE TYPE connectionstatus AS ENUM ('PENDING', 'ACCEPTED', 'REJECTED');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Create connections table
CREATE TABLE IF NOT EXISTS connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    teacher_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status connectionstatus NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_student_teacher UNIQUE (student_id, teacher_id)
);

CREATE INDEX IF NOT EXISTS idx_connections_student_id ON connections(student_id);
CREATE INDEX IF NOT EXISTS idx_connections_teacher_id ON connections(teacher_id);
CREATE INDEX IF NOT EXISTS idx_connections_status ON connections(status);

-- Ensure the update_updated_at_column function exists
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Auto-update trigger for connections
CREATE TRIGGER update_connections_updated_at BEFORE UPDATE ON connections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
