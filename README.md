# Aura - Universal Capture & Relational PKM Assistant

**Aura** is an all-in-one Personal Knowledge Management (PKM) system designed to solve the "capture problem." It provides a single, universal input interface that accepts any data type (text, audio, images, PDFs, links), and uses an AI assistant to analyze, clarify, and suggest organizational actions based on PARA/GTD methodologies.

## 🌟 Core Features

- **Universal Capture Interface**: Chat-like input accepting text, links, and file uploads (images, PDFs, audio, video)
- **AI-Suggested Organization**: AI analyzes content and suggests actions (never auto-files without confirmation)
- **Daily Notes as Timeline**: Permanent log with relational many-to-many linking
- **PARA System**: Projects, Areas, Resources, Archives with dynamic AI learning
- **Intelligent Processing**:
  - **Invoices/Documents**: OCR, extraction, task suggestions
  - **Audio/Video**: Transcription, summarization, task detection
  - **Links**: Article scraping, bookmarking, content analysis
  - **Pictures**: Metadata extraction, objective image analysis

## 🏗️ Architecture

### Technology Stack

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend API**: FastAPI + Python 3.11+
- **Database**: PostgreSQL 15+
- **AI Service**: Python (FastAPI) with LLM integration
- **Media Processing**: librosa, Pillow, pypdf, python-docx
- **ORM**: SQLAlchemy
- **Real-time**: WebSockets for chat interface

### Project Structure

```
aura/
├── frontend/           # React web application
├── backend/            # FastAPI backend API
├── ai-service/         # AI processing microservice
├── database/           # Database initialization
├── docs/               # Documentation
└── docker-compose.yml  # Local development setup
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Running with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd aura
```

2. Copy environment file and configure:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. Start all services:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- AI Service: http://localhost:8001

### Local Development (without Docker)

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

#### AI Service Setup

```bash
cd ai-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8001
```

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Database Schema](docs/DATABASE.md)
- [Development Setup](docs/SETUP.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)

## 🗄️ Database Setup

The PostgreSQL database is automatically initialized via Docker. For manual setup:

```bash
cd database
psql -U postgres -f init.sql
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🔐 Environment Variables

See `.env.example` for required environment variables. Key variables include:

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: For AI processing
- `JWT_SECRET_KEY`: For authentication
- `UPLOAD_DIR`: Media file storage location

## 📖 API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

## 🛠️ Development Roadmap

### Phase 1: MVP (Current)
- [x] Project structure and setup
- [ ] User authentication
- [ ] Basic note creation
- [ ] Daily notes interface
- [ ] PARA basic structure
- [ ] File upload and storage

### Phase 2: AI Processing
- [ ] Text extraction
- [ ] Audio transcription
- [ ] Image OCR/analysis
- [ ] PDF processing
- [ ] Chat interface

### Phase 3: Advanced Features
- [ ] Note linking system
- [ ] Full-text search with embeddings
- [ ] AI-powered suggestions
- [ ] Graph visualization
- [ ] Markdown export

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details on our code of conduct and development process.

## 📄 License

[License information to be added]

## 🙏 Acknowledgments

- Inspired by PARA method (Tiago Forte) and GTD (David Allen)
- Daily notes concept inspired by Capacities
- Built with modern web technologies and AI capabilities
