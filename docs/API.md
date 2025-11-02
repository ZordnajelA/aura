# Aura API Documentation

Base URL: `http://localhost:8000`

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### POST /api/auth/register

Register a new user.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### POST /api/auth/login

Login and receive access token.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response** (200):
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

## Notes

### GET /api/notes

List all notes for the authenticated user.

**Query Parameters**:
- `limit` (int): Number of results (default: 50)
- `offset` (int): Pagination offset (default: 0)
- `type` (string): Filter by note type

**Response** (200):
```json
{
  "notes": [
    {
      "id": "uuid",
      "title": "My Note",
      "content": "Note content...",
      "note_type": "text",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100
}
```

### POST /api/notes

Create a new note.

**Request**:
```json
{
  "title": "My Note",
  "content": "Note content...",
  "note_type": "text"
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "title": "My Note",
  "content": "Note content...",
  "note_type": "text",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET /api/notes/{id}

Get a specific note.

**Response** (200):
```json
{
  "id": "uuid",
  "title": "My Note",
  "content": "Note content...",
  "note_type": "text",
  "links": [
    {
      "id": "uuid",
      "title": "Related Note",
      "relation_type": "related"
    }
  ],
  "tags": ["tag1", "tag2"],
  "created_at": "2024-01-01T00:00:00Z"
}
```

### PUT /api/notes/{id}

Update a note.

**Request**:
```json
{
  "title": "Updated Title",
  "content": "Updated content..."
}
```

**Response** (200): Updated note object

### DELETE /api/notes/{id}

Delete a note.

**Response** (204): No content

## Daily Notes

### GET /api/daily/{date}

Get daily note for a specific date (format: YYYY-MM-DD).

**Response** (200):
```json
{
  "id": "uuid",
  "date": "2024-01-01",
  "content": "Daily note content...",
  "linked_notes": [
    {
      "id": "uuid",
      "title": "Captured Note",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### POST /api/daily

Create or update daily note for today.

**Request**:
```json
{
  "content": "Today's notes..."
}
```

**Response** (200): Daily note object

## Media Upload

### POST /api/media/upload

Upload a file (image, PDF, audio, video).

**Request**: `multipart/form-data`
- `file`: File to upload

**Response** (200):
```json
{
  "id": "uuid",
  "file_path": "/uploads/abc123.pdf",
  "file_type": "pdf",
  "file_size": 102400,
  "processing_job_id": "uuid"
}
```

### GET /api/media/{id}

Get media metadata and processing status.

**Response** (200):
```json
{
  "id": "uuid",
  "file_path": "/uploads/abc123.pdf",
  "file_type": "pdf",
  "is_processed": true,
  "processed_content": {
    "extracted_text": "...",
    "summary": "...",
    "metadata": {}
  }
}
```

## PARA Organization

### GET /api/para/areas

List all areas.

**Response** (200):
```json
{
  "areas": [
    {
      "id": "uuid",
      "name": "Health",
      "description": "Health and fitness",
      "icon": "heart",
      "display_order": 1
    }
  ]
}
```

### POST /api/para/areas

Create a new area.

**Request**:
```json
{
  "name": "Health",
  "description": "Health and fitness",
  "icon": "heart"
}
```

**Response** (201): Area object

### GET /api/para/projects

List all projects.

**Query Parameters**:
- `status` (string): Filter by status (active, completed, archived)
- `area_id` (uuid): Filter by area

**Response** (200):
```json
{
  "projects": [
    {
      "id": "uuid",
      "name": "Launch Product",
      "area_id": "uuid",
      "status": "active",
      "due_date": "2024-12-31"
    }
  ]
}
```

### POST /api/para/projects

Create a new project.

**Request**:
```json
{
  "name": "Launch Product",
  "area_id": "uuid",
  "description": "...",
  "due_date": "2024-12-31"
}
```

**Response** (201): Project object

### GET /api/para/resources

List all resources.

**Response** (200):
```json
{
  "resources": [
    {
      "id": "uuid",
      "title": "Article Title",
      "resource_type": "bookmark",
      "url": "https://example.com"
    }
  ]
}
```

## Links

### POST /api/links

Create a link between two notes.

**Request**:
```json
{
  "source_note_id": "uuid",
  "target_note_id": "uuid",
  "relation_type": "related"
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "source_note_id": "uuid",
  "target_note_id": "uuid",
  "relation_type": "related"
}
```

### GET /api/links/{note_id}

Get all links for a note.

**Response** (200):
```json
{
  "links": [
    {
      "id": "uuid",
      "target_note": {
        "id": "uuid",
        "title": "Related Note"
      },
      "relation_type": "related"
    }
  ]
}
```

## Chat (WebSocket)

### WS /api/chat

WebSocket endpoint for real-time chat interface.

**Send Message**:
```json
{
  "type": "message",
  "content": "User message..."
}
```

**Receive Message**:
```json
{
  "type": "assistant",
  "content": "AI response...",
  "suggestions": {
    "tasks": ["Call dentist"],
    "areas": ["Health"],
    "projects": []
  }
}
```

**Receive Processing Status**:
```json
{
  "type": "status",
  "job_id": "uuid",
  "status": "processing",
  "progress": 50
}
```

## AI Processing (Internal - AI Service)

These endpoints are called by the backend, not directly by frontend.

### POST /process/audio

Process audio file and return transcription.

### POST /process/image

Process image with OCR and analysis.

### POST /process/pdf

Extract text from PDF.

### POST /process/link

Scrape web content from URL.

### POST /analyze

Analyze content and generate PARA suggestions.

## Error Responses

All endpoints may return these error responses:

**400 Bad Request**:
```json
{
  "detail": "Validation error message"
}
```

**401 Unauthorized**:
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden**:
```json
{
  "detail": "Not authorized to access this resource"
}
```

**404 Not Found**:
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

(To be implemented in production)

- 100 requests per minute per user
- 1000 requests per hour per user

## Interactive Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation where you can test all endpoints.
