# Contributing to Aura

Thank you for your interest in contributing to Aura! This document provides guidelines and instructions for contributing.

## Development Process

1. **Fork the repository**
2. **Create a feature branch** from `main`
3. **Make your changes** with clear, focused commits
4. **Write or update tests** as needed
5. **Ensure all tests pass**
6. **Submit a pull request**

## Setting Up Development Environment

See [SETUP.md](./SETUP.md) for detailed setup instructions.

Quick start:
```bash
git clone <your-fork>
cd aura
cp .env.example .env
# Edit .env with your settings
docker-compose up -d
```

## Code Style

### Python (Backend & AI Service)

- Follow **PEP 8** style guide
- Use **Black** for formatting (line length: 88)
- Use **type hints** for function signatures
- Write **docstrings** for classes and functions

```python
def process_audio(file_path: str, options: dict | None = None) -> dict:
    """
    Process audio file and extract transcription.

    Args:
        file_path: Path to audio file
        options: Optional processing options

    Returns:
        Dictionary containing transcription and metadata
    """
    pass
```

Run linting:
```bash
cd backend
black app/
flake8 app/
mypy app/
```

### TypeScript/React (Frontend)

- Follow **ESLint** configuration
- Use **Prettier** for formatting
- Use **TypeScript** for type safety
- Write **functional components** with hooks

```typescript
interface CaptureProps {
  onSubmit: (content: string) => void
}

export default function CaptureInterface({ onSubmit }: CaptureProps) {
  // Component logic
}
```

Run linting:
```bash
cd frontend
npm run lint
npm run format
```

## Commit Messages

Follow the **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(backend): add audio transcription endpoint

Implement /api/media/process-audio endpoint using Whisper
for audio transcription. Includes error handling and
progress tracking.

Closes #42
```

```
fix(frontend): correct file upload validation

File upload was accepting invalid file types. Updated
validation to match backend allowed extensions.
```

## Testing

### Backend Tests

We use **pytest** for backend testing.

```bash
cd backend
pytest                          # Run all tests
pytest tests/test_notes.py     # Run specific test file
pytest -k "test_create"        # Run tests matching pattern
pytest --cov=app               # Run with coverage
```

Write tests in `backend/tests/`:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_note():
    response = client.post(
        "/api/notes",
        json={"title": "Test", "content": "Content"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test"
```

### Frontend Tests

We use **Vitest** for frontend testing.

```bash
cd frontend
npm test                        # Run all tests
npm test -- --watch            # Run in watch mode
npm test -- --coverage         # Run with coverage
```

Write tests alongside components:
```typescript
import { render, screen } from '@testing-library/react'
import CaptureInterface from './CaptureInterface'

test('renders input field', () => {
  render(<CaptureInterface />)
  expect(screen.getByPlaceholderText(/capture/i)).toBeInTheDocument()
})
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**: `pytest` and `npm test`
4. **Update CHANGELOG.md** if applicable
5. **Create PR** with clear description

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Manual testing performed

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

## Architecture Guidelines

### Backend Structure

```
backend/app/
├── api/          # Route handlers (thin layer)
├── models/       # SQLAlchemy models
├── schemas/      # Pydantic schemas
├── services/     # Business logic (fat layer)
└── utils/        # Helper functions
```

**Principles**:
- Keep **route handlers thin** - delegate to services
- Put **business logic in services**
- Use **dependency injection** for database sessions
- Handle **errors gracefully** with proper HTTP status codes

### Frontend Structure

```
frontend/src/
├── components/   # Reusable UI components
├── pages/        # Page-level components
├── services/     # API clients
├── hooks/        # Custom React hooks
├── types/        # TypeScript types
└── utils/        # Helper functions
```

**Principles**:
- **Component composition** over inheritance
- **Custom hooks** for reusable logic
- **React Query** for server state
- **Zustand** for client state
- **TypeScript** for all files

## Database Changes

Use **Alembic** for database migrations:

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Add tasks table"

# Review generated migration in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

**Guidelines**:
- Never modify `database/init.sql` directly for schema changes
- Always create migrations for schema changes
- Test migrations up AND down
- Include data migrations if needed

## Adding New Features

### Example: Adding a New Note Type

1. **Update database schema** (if needed):
```bash
# Update models/note.py to add new type validation
alembic revision --autogenerate -m "Add video note type"
```

2. **Create API endpoint**:
```python
# backend/app/api/notes.py
@router.post("/process-video")
async def process_video(file: UploadFile):
    # Implementation
```

3. **Add AI processing**:
```python
# ai-service/processors/video_processor.py
class VideoProcessor:
    def process(self, file_path: str) -> dict:
        # Implementation
```

4. **Update frontend**:
```typescript
// frontend/src/components/VideoUpload.tsx
export default function VideoUpload() {
  // Component implementation
}
```

5. **Write tests** for all layers
6. **Update documentation**

## Code Review Guidelines

### For Reviewers

- Be respectful and constructive
- Focus on code quality, not style (automated)
- Check for security issues
- Verify tests are adequate
- Suggest improvements, don't demand

### For Authors

- Respond to all comments
- Be open to feedback
- Make requested changes or explain reasoning
- Keep PRs focused and reasonably sized

## Reporting Bugs

Use GitHub Issues with the bug template:

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen

**Screenshots**
If applicable

**Environment**
- OS: [e.g., macOS 14]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 0.1.0]
```

## Feature Requests

Use GitHub Issues with the feature template:

```markdown
**Is your feature request related to a problem?**
Description

**Describe the solution you'd like**
Clear description

**Describe alternatives you've considered**
Other options

**Additional context**
Any other information
```

## Questions?

- Check existing documentation
- Search existing issues
- Join our discussions
- Ask in pull request if related to code

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing to Aura! 🙏
