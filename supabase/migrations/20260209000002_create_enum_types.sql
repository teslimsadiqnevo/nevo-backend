-- Create PostgreSQL enum types for SQLAlchemy models
-- SQLAlchemy uses enum member NAMES (uppercase) not values (lowercase)

-- Revert any VARCHAR columns to prepare for enum conversion
ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(50) USING role::VARCHAR;
ALTER TABLE assessments ALTER COLUMN status TYPE VARCHAR(50) USING status::VARCHAR;
ALTER TABLE neuro_profiles ALTER COLUMN learning_style TYPE VARCHAR(50) USING learning_style::VARCHAR;
ALTER TABLE neuro_profiles ALTER COLUMN reading_level TYPE VARCHAR(50) USING reading_level::VARCHAR;
ALTER TABLE neuro_profiles ALTER COLUMN complexity_tolerance TYPE VARCHAR(50) USING complexity_tolerance::VARCHAR;
ALTER TABLE lessons ALTER COLUMN status TYPE VARCHAR(50) USING status::VARCHAR;
ALTER TABLE adapted_lessons ALTER COLUMN status TYPE VARCHAR(50) USING status::VARCHAR;

-- Drop old enums if they exist
DROP TYPE IF EXISTS userrole;
DROP TYPE IF EXISTS assessmentstatus;
DROP TYPE IF EXISTS learningstyle;
DROP TYPE IF EXISTS readinglevel;
DROP TYPE IF EXISTS complexitytolerance;
DROP TYPE IF EXISTS lessonstatus;
DROP TYPE IF EXISTS adaptedlessonstatus;

-- Create enum types with UPPERCASE values (matching SQLAlchemy enum member names)
CREATE TYPE userrole AS ENUM ('STUDENT', 'TEACHER', 'SCHOOL_ADMIN', 'PARENT', 'SUPER_ADMIN');
CREATE TYPE assessmentstatus AS ENUM ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'PROCESSING');
CREATE TYPE learningstyle AS ENUM ('VISUAL', 'AUDITORY', 'KINESTHETIC', 'READING_WRITING', 'MULTIMODAL');
CREATE TYPE readinglevel AS ENUM ('PRE_K', 'GRADE_1', 'GRADE_2', 'GRADE_3', 'GRADE_4', 'GRADE_5', 'GRADE_6', 'GRADE_7', 'GRADE_8', 'HIGH_SCHOOL');
CREATE TYPE complexitytolerance AS ENUM ('LOW', 'MEDIUM', 'HIGH');
CREATE TYPE lessonstatus AS ENUM ('DRAFT', 'PUBLISHED', 'ARCHIVED');
CREATE TYPE adaptedlessonstatus AS ENUM ('PENDING', 'GENERATING', 'READY', 'FAILED');

-- Convert columns to enum types
ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole;
ALTER TABLE assessments ALTER COLUMN status TYPE assessmentstatus USING status::assessmentstatus;
ALTER TABLE neuro_profiles ALTER COLUMN learning_style TYPE learningstyle USING learning_style::learningstyle;
ALTER TABLE neuro_profiles ALTER COLUMN reading_level TYPE readinglevel USING reading_level::readinglevel;
ALTER TABLE neuro_profiles ALTER COLUMN complexity_tolerance TYPE complexitytolerance USING complexity_tolerance::complexitytolerance;
ALTER TABLE lessons ALTER COLUMN status TYPE lessonstatus USING status::lessonstatus;
ALTER TABLE adapted_lessons ALTER COLUMN status TYPE adaptedlessonstatus USING status::adaptedlessonstatus;
