-- Teacher feedback table for encouragement messages from teachers to students
CREATE TABLE IF NOT EXISTS teacher_feedbacks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_id UUID REFERENCES lessons(id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_teacher_feedbacks_student ON teacher_feedbacks(student_id);
CREATE INDEX IF NOT EXISTS idx_teacher_feedbacks_teacher ON teacher_feedbacks(teacher_id);
