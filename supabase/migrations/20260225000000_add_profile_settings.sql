-- Add accessibility preference columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS voice_guidance BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS large_text BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS extra_spacing BOOLEAN NOT NULL DEFAULT false;
