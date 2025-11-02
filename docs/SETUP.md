# Development Setup Guide

This guide will help you set up your local development environment for Aura.

## Prerequisites

Ensure you have the following installed:

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Node.js** (18+) and **npm** (9+) for local frontend development
- **Python** (3.11+) for local backend development
- **Git**

## Quick Start with Docker

This is the easiest way to get started with all services running.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd aura
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required for AI processing
OPENAI_API_KEY=sk-your-openai-key
# OR
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Update JWT secret for production
JWT_SECRET_KEY=your-super-secret-key-change-this
```

### 3. Start All Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Redis on port 6379
- Backend API on port 8000
- AI Service on port 8001
- Frontend on port 3000

### 4. Verify Services

Check that all services are running:

```bash
docker-compose ps
```

Access the services:
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **AI Service Docs**: http://localhost:8001/docs

### 5. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f ai-service
```

## Local Development (Without Docker)

For faster iteration, you can run services locally.

### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up PostgreSQL** (if not using Docker):
```bash
# Install PostgreSQL locally or use Docker for just the database
docker run -d \
  --name aura-postgres \
  -e POSTGRES_USER=aura_user \
  -e POSTGRES_PASSWORD=aura_password \
  -e POSTGRES_DB=aura_db \
  -p 5432:5432 \
  postgres:15-alpine
```

5. **Initialize database**:
```bash
# Apply migrations or run init script
psql -U aura_user -d aura_db -f ../database/init.sql
```

6. **Run backend**:
```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at http://localhost:8000

### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Configure environment**:
```bash
# Create .env.local
echo "VITE_API_URL=http://localhost:8000/api" > .env.local
echo "VITE_WS_URL=ws://localhost:8000/ws" >> .env.local
```

4. **Run frontend**:
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

### AI Service Setup

1. **Navigate to ai-service directory**:
```bash
cd ai-service
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate
```

3. **Install system dependencies** (for audio/image processing):

**macOS**:
```bash
brew install ffmpeg tesseract poppler
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg tesseract-ocr poppler-utils
```

**Windows**:
- Download and install FFmpeg from https://ffmpeg.org/download.html
- Download and install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki

4. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

5. **Download Whisper model** (optional, done at runtime):
```bash
python -c "import whisper; whisper.load_model('base')"
```

6. **Run AI service**:
```bash
uvicorn app:app --reload --port 8001
```

AI Service will be available at http://localhost:8001

## Database Management

### Viewing the Database

Using `psql`:
```bash
docker exec -it aura-postgres psql -U aura_user -d aura_db
```

Using a GUI tool:
- **Connection**: localhost:5432
- **Database**: aura_db
- **User**: aura_user
- **Password**: aura_password

### Running Migrations

We use Alembic for database migrations.

1. **Create a migration**:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

2. **Apply migrations**:
```bash
alembic upgrade head
```

3. **Rollback**:
```bash
alembic downgrade -1
```

### Resetting the Database

```bash
# Stop all services
docker-compose down

# Remove database volume
docker volume rm aura_postgres-data

# Start services (database will be recreated)
docker-compose up -d
```

## Testing

### Backend Tests

```bash
cd backend
pytest
```

With coverage:
```bash
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Common Issues

### Port Already in Use

If you get "port already in use" errors:

```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or change the port in docker-compose.yml
```

### Database Connection Failed

1. Check PostgreSQL is running:
```bash
docker-compose ps postgres
```

2. Check connection settings in `.env`

3. Verify network connectivity:
```bash
docker exec -it aura-backend ping postgres
```

### AI Service Out of Memory

Whisper models can be memory-intensive. Use a smaller model:

In `.env`:
```bash
WHISPER_MODEL=tiny  # Options: tiny, base, small, medium, large
```

### Frontend Not Connecting to Backend

1. Check CORS settings in `backend/app/config.py`
2. Verify `VITE_API_URL` in frontend `.env.local`
3. Check network tab in browser dev tools for errors

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- Docker

Workspace settings (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

### PyCharm

1. Mark `backend/app` as Sources Root
2. Configure Python interpreter to use virtual environment
3. Enable Django support for better autocomplete

## Environment Variables Reference

See `.env.example` for full list of available environment variables.

**Required**:
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

**Optional**:
- `REDIS_URL` (for task queue)
- `SMTP_*` (for email notifications)
- `WHISPER_MODEL` (audio transcription model size)

## Next Steps

- Read [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- Read [API.md](./API.md) for API documentation
- Check [DATABASE.md](./DATABASE.md) for schema details

## Getting Help

- Check existing issues on GitHub
- Review logs: `docker-compose logs -f`
- Verify all services are healthy: `docker-compose ps`
