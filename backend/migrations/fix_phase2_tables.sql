-- Complete fix for Phase 2 tables
-- This script drops and recreates the tables with the correct schema

BEGIN;

-- Drop existing tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS text_classifications CASCADE;
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS processed_content CASCADE;
DROP TABLE IF EXISTS processing_jobs CASCADE;

-- Create processing_jobs table
CREATE TABLE processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    media_id UUID REFERENCES media(id) ON DELETE CASCADE,
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    progress INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_processing_jobs_user_id ON processing_jobs(user_id);
CREATE INDEX idx_processing_jobs_media_id ON processing_jobs(media_id);
CREATE INDEX idx_processing_jobs_note_id ON processing_jobs(note_id);
CREATE INDEX idx_processing_jobs_status ON processing_jobs(status);

-- Create processed_content table
CREATE TABLE processed_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    processing_job_id UUID NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL,
    raw_text TEXT,
    summary TEXT,
    key_points TEXT,
    extracted_tasks TEXT,
    metadata TEXT,
    confidence_score INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_processed_content_note_id ON processed_content(note_id);
CREATE INDEX idx_processed_content_job_id ON processed_content(processing_job_id);

-- Create chat_messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    context_notes TEXT,
    suggestions TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);

-- Create text_classifications table
CREATE TABLE text_classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    classification_type VARCHAR(50) NOT NULL,
    confidence INTEGER NOT NULL,
    suggested_area VARCHAR(255),
    suggested_project VARCHAR(255),
    is_actionable BOOLEAN NOT NULL DEFAULT FALSE,
    priority VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_text_classifications_note_id ON text_classifications(note_id);

COMMIT;

-- Verify tables were created correctly
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name IN ('processing_jobs', 'processed_content', 'chat_messages', 'text_classifications')
ORDER BY table_name, ordinal_position;
