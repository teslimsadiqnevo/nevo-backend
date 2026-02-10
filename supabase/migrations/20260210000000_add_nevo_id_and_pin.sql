-- Add Nevo ID and PIN hash columns to users table
-- Nevo ID: Unique student identifier for tablet-friendly login (format: NEVO-XXXXX)
-- PIN hash: bcrypt-hashed 4-digit PIN for Nevo ID login

ALTER TABLE users ADD COLUMN IF NOT EXISTS nevo_id VARCHAR(10) UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS pin_hash VARCHAR(255);

-- Partial unique index: only enforces uniqueness on non-null values
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_nevo_id ON users(nevo_id) WHERE nevo_id IS NOT NULL;
