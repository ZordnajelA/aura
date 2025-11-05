-- Migration: Add Phase 2 AI Processing Tables
-- Run this SQL script to manually create the Phase 2 tables

-- Table: processing_jobs
CREATE TABLE IF NOT EXISTS processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    media_id UUID REFERENCES media(id) ON DELETE CASCADE,
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL,  -- audio, video, image, document, text_classification
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- pending, processing, completed, failed
    progress INTEGER NOT NULL DEFAULT 0,  -- 0-100
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_processing_jobs_user_id ON processing_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_media_id ON processing_jobs(media_id);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_note_id ON processing_jobs(note_id);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);

-- Table: processed_content
CREATE TABLE IF NOT EXISTS processed_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    processing_job_id UUID NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL,  -- transcription, ocr, document_text, summary, classification
    raw_text TEXT,
    summary TEXT,
    key_points TEXT,  -- JSON array stored as text
    extracted_tasks TEXT,  -- JSON array stored as text
    metadata TEXT,  -- JSON stored as text
    confidence_score INTEGER,  -- 0-100
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_processed_content_note_id ON processed_content(note_id);
CREATE INDEX IF NOT EXISTS idx_processed_content_job_id ON processed_content(processing_job_id);

-- Table: chat_messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID NOT NULL,
    role VARCHAR(50) NOT NULL,  -- user, assistant, system
    content TEXT NOT NULL,
    context_notes TEXT,  -- JSON array of note IDs
    suggestions TEXT,  -- JSON array of suggestion objects
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);

-- Table: text_classifications
CREATE TABLE IF NOT EXISTS text_classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    classification_type VARCHAR(50) NOT NULL,  -- task, log_entry, thought, meeting_note, invoice, email, reference, other
    confidence INTEGER NOT NULL,  -- 0-100
    suggested_area VARCHAR(255),
    suggested_project VARCHAR(255),
    is_actionable BOOLEAN NOT NULL DEFAULT FALSE,
    priority VARCHAR(50),  -- low, medium, high, urgent
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_text_classifications_note_id ON text_classifications(note_id);

-- Verify tables were created
SELECT
    tablename,
    schemaname
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('processing_jobs', 'processed_content', 'chat_messages', 'text_classifications')
ORDER BY tablename;
