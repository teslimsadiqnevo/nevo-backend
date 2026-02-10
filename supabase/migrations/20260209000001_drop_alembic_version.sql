-- Remove legacy Alembic migration tracking table (replaced by Supabase CLI)
DROP TABLE IF EXISTS alembic_version;
