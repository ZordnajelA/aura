# Database Schema Documentation

## Overview

Aura uses PostgreSQL as its primary database with a relational schema designed to support:
- Many-to-many note linking
- PARA organizational structure
- Daily notes as permanent timeline
- Full-text search
- Vector embeddings for semantic search (future)

## Entity Relationship Diagram

```
users
  ├── notes (1:many)
  │   ├── media (1:many)
  │   │   └── processed_content (1:1)
  │   ├── note_links (many:many self-reference)
  │   ├── note_tags (many:many via tags)
  │   └── daily_note_links (many:many via daily_notes)
  ├── daily_notes (1:many)
  ├── areas (1:many)
  │   ├── projects (1:many)
  │   └── resources (1:many)
  ├── tasks (1:many)
  ├── tags (1:many)
  ├── chat_messages (1:many)
  └── processing_jobs (1:many)
```

## Core Tables

### users

Stores user accounts and authentication information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | User identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password |
| created_at | TIMESTAMP | DEFAULT NOW() | Account creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

### notes

Central table storing all captured content.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Note identifier |
| user_id | UUID | FK(users), NOT NULL | Owner |
| title | VARCHAR(500) | | Note title |
| content | TEXT | | Note content |
| note_type | VARCHAR(50) | DEFAULT 'text' | text, audio, image, pdf, link |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

**Indexes**:
- `idx_notes_user_id` on `user_id`
- `idx_notes_created_at` on `created_at DESC`
- `idx_notes_content_fts` GIN full-text search on `content`
- `idx_notes_title_fts` GIN full-text search on `title`

### daily_notes

Timeline/log of daily activities. Core of Model B architecture.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Daily note identifier |
| user_id | UUID | FK(users), NOT NULL | Owner |
| note_date | DATE | NOT NULL | Date of daily note |
| content | TEXT | | Daily note content |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

**Unique Constraint**: `(user_id, note_date)` - one daily note per user per day

**Indexes**:
- `idx_daily_notes_user_date` on `(user_id, note_date DESC)`

## Media Tables

### media

Metadata for uploaded files.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Media identifier |
| note_id | UUID | FK(notes), CASCADE | Associated note |
| file_path | VARCHAR(1000) | NOT NULL | Path to file |
| file_type | VARCHAR(100) | NOT NULL | File extension |
| file_size | BIGINT | | File size in bytes |
| mime_type | VARCHAR(100) | | MIME type |
| is_processed | BOOLEAN | DEFAULT FALSE | Processing status |
| created_at | TIMESTAMP | DEFAULT NOW() | Upload time |

**Indexes**:
- `idx_media_note_id` on `note_id`

### processed_content

Results from AI processing (OCR, transcription, etc.).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Record identifier |
| media_id | UUID | FK(media), CASCADE | Source media |
| extracted_text | TEXT | | Extracted text content |
| summary | TEXT | | AI-generated summary |
| metadata | JSONB | | Additional metadata |
| embeddings | VECTOR(1536) | | Vector embeddings (requires pgvector) |
| created_at | TIMESTAMP | DEFAULT NOW() | Processing time |

## PARA Tables

### areas

Ongoing responsibilities (PARA: Areas).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Area identifier |
| user_id | UUID | FK(users), NOT NULL | Owner |
| name | VARCHAR(255) | NOT NULL | Area name |
| description | TEXT | | Description |
| icon | VARCHAR(50) | | Icon identifier |
| display_order | INTEGER | DEFAULT 0 | Sort order |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

### projects

Goal-oriented projects (PARA: Projects).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Project identifier |
| user_id | UUID | FK(users), NOT NULL | Owner |
| area_id | UUID | FK(areas), SET NULL | Associated area |
| name | VARCHAR(255) | NOT NULL | Project name |
| description | TEXT | | Description |
| status | VARCHAR(50) | DEFAULT 'active' | active, completed, archived |
| due_date | DATE | | Target completion date |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

### resources

Reference materials (PARA: Resources).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Resource identifier |
| user_id | UUID | FK(users), NOT NULL | Owner |
| area_id | UUID | FK(areas), SET NULL | Associated area |
| title | VARCHAR(500) | NOT NULL | Resource title |
| content | TEXT | | Resource content |
| resource_type | VARCHAR(50) | DEFAULT 'note' | note, bookmark, file |
| url | VARCHAR(1000) | | URL if bookmark |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

### archives

Archived items from any PARA category (PARA: Archives).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Archive identifier |
| user_id | UUID | FK(users), NOT NULL | Owner |
| parent_type | VARCHAR(50) | NOT NULL | project, area, resource, note |
| parent_id | UUID | NOT NULL | Original item ID |
| archived_at | TIMESTAMP | DEFAULT NOW() | Archive time |
| metadata | JSONB | | Additional context |

## Linking Tables

### note_links

Many-to-many relationships between notes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Link identifier |
| source_note_id | UUID | FK(notes), CASCADE | Source note |
| target_note_id | UUID | FK(notes), CASCADE | Target note |
| relation_type | VARCHAR(50) | DEFAULT 'related' | Relationship type |
| created_at | TIMESTAMP | DEFAULT NOW() | Link creation time |

**Unique Constraint**: `(source_note_id, target_note_id, relation_type)`

**Indexes**:
- `idx_note_links_source` on `source_note_id`
- `idx_note_links_target` on `target_note_id`

**Relation Types**:
- `related` - General relationship
- `references` - Source references target
- `depends_on` - Source depends on target
- `parent_of` / `child_of` - Hierarchical

### daily_note_links

Links between daily notes and captured notes (Model B).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Link identifier |
| daily_note_id | UUID | FK(daily_notes), CASCADE | Daily note |
| note_id | UUID | FK(notes), CASCADE | Captured note |
| created_at | TIMESTAMP | DEFAULT NOW() | Link time |

**Unique Constraint**: `(daily_note_id, note_id)`

### tags

User-defined tags.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Tag identifier |
| user_id | UUID | FK(users), NOT NULL | Owner |
| name | VARCHAR(100) | NOT NULL | Tag name |
| color | VARCHAR(20) | | Display color |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |

**Unique Constraint**: `(user_id, name)`

### note_tags

Many-to-many relationship between notes and tags.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Record identifier |
| note_id | UUID | FK(notes), CASCADE | Note |
| tag_id | UUID | FK(tags), CASCADE | Tag |
| created_at | TIMESTAMP | DEFAULT NOW() | Tag application time |

**Unique Constraint**: `(note_id, tag_id)`

## Supporting Tables

### tasks

Extracted or created action items.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Task identifier |
| user_id | UUID | FK(users), NOT NULL | Owner |
| project_id | UUID | FK(projects), SET NULL | Associated project |
| title | VARCHAR(500) | NOT NULL | Task title |
| description | TEXT | | Task details |
| status | VARCHAR(50) | DEFAULT 'pending' | Task status |
| priority | VARCHAR(20) | DEFAULT 'medium' | Priority level |
| due_date | TIMESTAMP | | Due date/time |
| completed_at | TIMESTAMP | | Completion time |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

**Indexes**:
- `idx_tasks_user_id` on `user_id`
- `idx_tasks_status` on `status`

**Status Values**: `pending`, `in_progress`, `completed`, `cancelled`
**Priority Values**: `low`, `medium`, `high`, `urgent`

### chat_messages

Chat history for conversational interface.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Message identifier |
| user_id | UUID | FK(users), NOT NULL | User |
| role | VARCHAR(20) | NOT NULL | Message role |
| content | TEXT | NOT NULL | Message content |
| metadata | JSONB | | Additional data |
| created_at | TIMESTAMP | DEFAULT NOW() | Message time |

**Indexes**:
- `idx_chat_messages_user_id` on `(user_id, created_at DESC)`

**Role Values**: `user`, `assistant`, `system`

### processing_jobs

Track AI processing status for async operations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Job identifier |
| note_id | UUID | FK(notes), CASCADE | Associated note |
| media_id | UUID | FK(media), CASCADE | Associated media |
| status | VARCHAR(50) | DEFAULT 'pending' | Job status |
| progress | INTEGER | DEFAULT 0 | Progress percentage |
| result | JSONB | | Processing results |
| error_message | TEXT | | Error if failed |
| created_at | TIMESTAMP | DEFAULT NOW() | Job creation time |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last status update |

**Status Values**: `pending`, `processing`, `completed`, `failed`

## Triggers

### update_updated_at_column()

Automatically updates `updated_at` timestamp on row updates.

Applied to:
- notes
- daily_notes
- projects
- areas
- tasks

## Future Enhancements

1. **pgvector Extension**: Enable vector similarity search for semantic note discovery
2. **Partitioning**: Partition large tables (notes, chat_messages) by date for performance
3. **Materialized Views**: Pre-compute expensive queries (note graphs, statistics)
4. **Row-Level Security**: Additional security layer for multi-tenant setups

## Backup Strategy

(To be implemented in production)

1. **Daily Backups**: Full PostgreSQL dump
2. **WAL Archiving**: Continuous incremental backup
3. **Retention**: 30 days of daily backups
