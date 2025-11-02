# Aura Architecture Documentation

## System Overview

Aura is a microservices-based Personal Knowledge Management (PKM) system designed around the principle of **universal capture** and **relational linking**. The architecture follows a three-tier approach with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  - Chat-like capture interface                          │
│  - Daily notes view                                      │
│  - PARA organization UI                                  │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/WebSocket
┌────────────────▼────────────────────────────────────────┐
│              Backend API (FastAPI)                       │
│  - Authentication & authorization                        │
│  - Note CRUD operations                                  │
│  - PARA structure management                             │
│  - WebSocket chat handler                                │
└────────────┬───────────────────────────┬─────────────────┘
             │                           │
             │ PostgreSQL                │ HTTP
             │                           │
┌────────────▼────────┐    ┌─────────────▼──────────────┐
│   PostgreSQL DB      │    │   AI Service (Python)      │
│  - Relational data   │    │  - Audio transcription     │
│  - Note links        │    │  - OCR processing          │
│  - PARA structure    │    │  - PDF extraction          │
│  - Full-text search  │    │  - Web scraping            │
└──────────────────────┘    │  - LLM analysis            │
                            │  - PARA suggestions        │
                            └────────────────────────────┘
```

## Core Components

### 1. Frontend (React + TypeScript + Vite)

**Location**: `/frontend`

**Purpose**: User interface for universal capture and knowledge organization

**Key Features**:
- Chat-like input interface with file upload support
- Daily notes timeline view
- PARA buckets visualization
- Real-time AI processing status
- Note linking and graph visualization

**Tech Stack**:
- React 18 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- React Query for server state
- Zustand for client state
- Axios for HTTP requests

### 2. Backend API (FastAPI + Python)

**Location**: `/backend`

**Purpose**: Main application server handling business logic and data persistence

**Key Features**:
- RESTful API endpoints
- WebSocket support for real-time chat
- Authentication and authorization (JWT)
- File upload and storage management
- Database operations via SQLAlchemy ORM
- Coordination with AI service

**Tech Stack**:
- FastAPI for API framework
- SQLAlchemy 2.0 for ORM
- PostgreSQL for database
- Alembic for migrations
- Pydantic for validation

**API Structure**:
```
/api/auth       - Authentication endpoints
/api/notes      - Note CRUD operations
/api/daily      - Daily notes management
/api/media      - File upload and retrieval
/api/para       - PARA structure (Areas, Projects, Resources, Archives)
/api/links      - Note relationship management
/api/chat       - WebSocket chat interface
```

### 3. AI Processing Service (Python)

**Location**: `/ai-service`

**Purpose**: Specialized microservice for AI-powered content processing

**Key Features**:
- Audio transcription (Whisper)
- Image OCR (Tesseract)
- PDF text extraction
- Web content scraping
- LLM-based analysis (OpenAI GPT / Anthropic Claude)
- PARA suggestion generation

**Processing Pipeline**:
1. Receive file or content from backend
2. Extract raw content (transcribe, OCR, parse)
3. Generate summary (~500 characters)
4. Analyze for tasks, projects, entities
5. Generate PARA suggestions
6. Return structured results to backend

**Tech Stack**:
- FastAPI for service API
- OpenAI Whisper for audio transcription
- Tesseract for OCR
- OpenAI/Anthropic APIs for LLM analysis
- BeautifulSoup/Newspaper3k for web scraping

### 4. Database (PostgreSQL)

**Location**: `/database`

**Purpose**: Persistent storage with relational and full-text search capabilities

**Schema Design**:

**Core Tables**:
- `users` - User accounts
- `notes` - All captured content
- `daily_notes` - Daily timeline entries
- `media` - File metadata
- `processed_content` - Extracted text and embeddings

**PARA Tables**:
- `areas` - Ongoing responsibilities
- `projects` - Active projects with goals
- `resources` - Reference materials
- `archives` - Completed items

**Linking Tables**:
- `note_links` - Many-to-many note relationships
- `daily_note_links` - Links from daily notes to other notes
- `note_tags` - Tag associations

**Supporting Tables**:
- `tasks` - Extracted action items
- `tags` - User-defined tags
- `chat_messages` - Chat history
- `processing_jobs` - AI processing status

## Data Flow

### Capture Flow (User adds content)

```
1. User inputs text or uploads file via frontend
2. Frontend sends to backend /api/notes
3. Backend:
   - Saves note to database
   - Uploads file to storage
   - Creates media record
   - Triggers AI processing job
4. Backend calls AI service asynchronously
5. AI service:
   - Processes content (transcribe/OCR/parse)
   - Generates summary
   - Analyzes for PARA suggestions
   - Returns results
6. Backend:
   - Updates note with processed content
   - Sends suggestions via WebSocket to frontend
7. Frontend displays AI suggestions to user
8. User confirms/edits suggestions
9. Backend creates links, tasks, and PARA associations
```

### Daily Note Linking (Model B)

**Key Principle**: Notes are **never moved or duplicated**, only linked.

When a note is captured:
1. A `daily_note` record exists or is created for today
2. A `daily_note_links` entry links the note to today's daily note
3. Additional links created based on user confirmation:
   - Link to Area via `note_links`
   - Link to Project via `note_links`
   - Link to Resource via `note_links`
   - Create task in `tasks` table with `note_id` reference

**Result**: One note, multiple relationships. Accessible from:
- Today's daily note
- Associated area/project/resource
- Task list
- Tag search
- Full-text search

## AI Processing Rules

### Audio/Video
1. **Transcribe** using Whisper
2. **Generate summary** (~500 chars)
3. **Analyze** for tasks, ideas, entities
4. **Suggest**: Tasks, Projects, Areas to link

### Images
1. **Extract metadata** (EXIF: location, time, date)
2. **Run OCR** if text detected
3. **Analyze image** objectively (no artistic interpretation)
4. **Suggest**: Context-based areas or projects

### PDFs/Documents
1. **Extract text** using pypdf/python-docx
2. **Detect document type** (invoice, receipt, article)
3. **Extract entities** (vendor, amount, due date for invoices)
4. **Suggest**: Tasks (e.g., "Pay invoice"), Areas (e.g., "Finances")

### Links (Articles/Videos)
1. **Scrape content** or get video transcript
2. **Save URL** as bookmark
3. **Generate summary** (~500 chars)
4. **Analyze content**
5. **Suggest**: Projects/Resources to file under

## Security Considerations

1. **Authentication**: JWT-based with access/refresh tokens
2. **Authorization**: User-scoped data access via `user_id`
3. **File Upload**: Validation of file types, size limits
4. **API Keys**: AI service keys stored in environment, not in database
5. **CORS**: Configured origins in backend
6. **SQL Injection**: Prevented via SQLAlchemy ORM

## Scalability Considerations

### Current Architecture (MVP)
- Single backend instance
- Single AI service instance
- Monolithic PostgreSQL database

### Future Enhancements
1. **Horizontal Scaling**:
   - Multiple backend instances behind load balancer
   - Multiple AI service instances with task queue (Celery + Redis)

2. **Caching**:
   - Redis for session storage
   - Cache frequently accessed notes and PARA structure

3. **Search Optimization**:
   - Elasticsearch or Meilisearch for full-text search
   - Vector database (Pinecone, Weaviate) for semantic search

4. **File Storage**:
   - Move from local storage to S3/Cloud Storage
   - CDN for media delivery

5. **Database Optimization**:
   - Read replicas for queries
   - Partitioning for large tables (notes, chat_messages)

## Technology Choices

### Why FastAPI?
- Native async support
- Excellent performance
- Auto-generated API docs (OpenAPI)
- Type safety with Pydantic
- Easy integration with ML/AI libraries

### Why React?
- Component-based architecture
- Large ecosystem
- Excellent TypeScript support
- Chat-like UI components readily available

### Why PostgreSQL?
- Relational data for note linking
- Full-text search built-in
- JSONB for flexible metadata
- pgvector extension for embeddings
- Strong consistency guarantees

### Why Microservices for AI?
- Heavy processing isolated from main API
- Independent scaling
- Can swap AI providers easily
- Easier to add GPU resources if needed

## Development Workflow

1. **Local Development**: Docker Compose brings up all services
2. **Database Migrations**: Alembic manages schema changes
3. **Testing**: Pytest for backend, Vitest for frontend
4. **API Documentation**: Auto-generated at `/docs`
5. **Type Safety**: TypeScript frontend, Pydantic backend

## Next Steps

See [SETUP.md](./SETUP.md) for development environment setup instructions.
