# Aura AI Service

AI processing microservice for Aura PKM system. Handles transcription, OCR, content analysis, and intelligent PARA suggestions.

## Features

- **Multi-Provider LLM Support**: Google Gemini (primary), OpenAI GPT, Anthropic Claude
- **Audio Processing**: Transcription using OpenAI Whisper
- **Image Processing**: OCR using Tesseract
- **PDF Processing**: Text extraction
- **Web Scraping**: Article and video content extraction
- **Content Analysis**: AI-powered PARA suggestions

## Configuration

### Choosing an AI Provider

Aura supports multiple LLM providers. Configure your preferred provider in `.env`:

#### Option 1: Google Gemini (Recommended)

```bash
DEFAULT_LLM_PROVIDER=gemini
GOOGLE_API_KEY=your-google-api-key
GEMINI_MODEL=gemini-1.5-flash  # or gemini-1.5-pro
```

**Get your API key**: https://makersuite.google.com/app/apikey

**Available models**:
- `gemini-1.5-flash` - Fast, cost-effective (recommended for most use cases)
- `gemini-1.5-pro` - Most capable, higher quality
- `gemini-pro` - Legacy model

#### Option 2: OpenAI GPT

```bash
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview  # or gpt-3.5-turbo
```

**Get your API key**: https://platform.openai.com/api-keys

**Available models**:
- `gpt-4-turbo-preview` - Most capable
- `gpt-4` - Stable GPT-4
- `gpt-3.5-turbo` - Fast and cost-effective

#### Option 3: Anthropic Claude

```bash
DEFAULT_LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

**Get your API key**: https://console.anthropic.com/

**Available models**:
- `claude-3-5-sonnet-20241022` - Best overall (recommended)
- `claude-3-opus-20240229` - Most capable
- `claude-3-sonnet-20240229` - Balanced
- `claude-3-haiku-20240307` - Fast and economical

### Multi-Provider Setup

You can configure multiple providers and switch between them:

```bash
# Set all API keys
GOOGLE_API_KEY=your-google-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Choose default
DEFAULT_LLM_PROVIDER=gemini  # or openai, anthropic
```

The service will automatically fall back to available providers if the default fails.

## Installation

### Using Docker (Recommended)

The AI service is included in the main `docker-compose.yml`:

```bash
docker-compose up ai-service
```

### Local Development

1. **Install system dependencies**:

**macOS**:
```bash
brew install ffmpeg tesseract poppler
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg tesseract-ocr poppler-utils
```

2. **Install Python dependencies**:
```bash
cd ai-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp ../.env.example .env
# Edit .env with your API keys
```

4. **Run the service**:
```bash
uvicorn app:app --reload --port 8001
```

## API Endpoints

### Health Check

```bash
GET /health
```

### Process Audio

```bash
POST /process/audio
Content-Type: multipart/form-data

file: <audio_file>
```

**Response**:
```json
{
  "success": true,
  "media_type": "audio",
  "extracted_text": "Transcribed text...",
  "summary": "Summary of audio content...",
  "suggestions": {
    "tasks": ["Call dentist tomorrow"],
    "projects": ["Health Tracking"],
    "areas": ["Health"]
  }
}
```

### Process Image

```bash
POST /process/image
Content-Type: multipart/form-data

file: <image_file>
```

### Process PDF

```bash
POST /process/pdf
Content-Type: multipart/form-data

file: <pdf_file>
```

### Process Link

```bash
POST /process/link
Content-Type: application/json

{
  "file_path": "https://example.com/article",
  "media_type": "link"
}
```

### Analyze Content

```bash
POST /analyze
Content-Type: application/json

{
  "file_path": "content text...",
  "media_type": "text",
  "options": {}
}
```

## Usage in Code

### LLM Service

```python
from services import get_llm_service

# Get default LLM service
llm = get_llm_service()

# Generate text
response = llm.generate("Explain quantum computing", max_tokens=500)

# Analyze content for PARA suggestions
analysis = llm.analyze_content(
    content="I need to call the dentist tomorrow about my appointment",
    content_type="text"
)
# Returns: {
#   "summary": "Reminder to contact dentist...",
#   "tasks": ["Call dentist tomorrow"],
#   "areas": ["Health"],
#   ...
# }

# Extract tasks
tasks = llm.extract_tasks("Buy milk, schedule meeting, review proposal")
# Returns: ["Buy milk", "Schedule meeting", "Review proposal"]

# Use specific provider
llm_openai = get_llm_service(provider="openai")
```

## Audio Transcription

Aura uses OpenAI Whisper for audio transcription. Configure the model size:

```bash
WHISPER_MODEL=base  # Options: tiny, base, small, medium, large
```

**Model sizes**:
- `tiny` - Fastest, lowest quality (~1GB RAM)
- `base` - Good balance (default, ~1GB RAM)
- `small` - Better quality (~2GB RAM)
- `medium` - High quality (~5GB RAM)
- `large` - Best quality (~10GB RAM)

Larger models are more accurate but require more memory and processing time.

## OCR Configuration

Tesseract OCR settings:

```bash
TESSERACT_LANG=eng  # Language code (eng, fra, deu, etc.)
OCR_DPI=300         # DPI for image processing
```

## Supported File Types

- **Audio**: mp3, wav, m4a, ogg, flac
- **Images**: jpg, jpeg, png, gif, bmp, tiff
- **Documents**: pdf, docx, txt
- **Video**: mp4, webm, avi (extracts audio for transcription)

## Performance Tuning

### Memory Usage

For limited memory environments:

```bash
# Use smaller Whisper model
WHISPER_MODEL=tiny

# Use Gemini Flash instead of Pro
GEMINI_MODEL=gemini-1.5-flash
```

### Processing Speed

For faster processing:

```bash
# Use fastest models
WHISPER_MODEL=tiny
GEMINI_MODEL=gemini-1.5-flash
```

### Cost Optimization

**Free tier options**:
- Google Gemini: Generous free tier (1500 requests/day for Gemini Flash)
- OpenAI: Requires payment, but GPT-3.5-turbo is inexpensive
- Anthropic: Requires payment

**Recommended for budget**:
```bash
DEFAULT_LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-1.5-flash
```

## Troubleshooting

### "GOOGLE_API_KEY not set"

Make sure your `.env` file has:
```bash
GOOGLE_API_KEY=your-actual-api-key
```

### "Module not found: google.generativeai"

Install the package:
```bash
pip install google-generativeai
```

### Whisper model download fails

The model downloads automatically on first use. Ensure internet connection and sufficient disk space (~1-10GB depending on model).

### Tesseract not found

Install Tesseract OCR:
```bash
# macOS
brew install tesseract

# Ubuntu
sudo apt-get install tesseract-ocr
```

## Development

### Running Tests

```bash
pytest tests/
```

### Adding a New Processor

1. Create processor in `processors/`:
```python
# processors/new_processor.py
class NewProcessor:
    def process(self, file_path: str) -> dict:
        # Implementation
        return {"extracted_text": "..."}
```

2. Add endpoint in `app.py`:
```python
@app.post("/process/new")
async def process_new(file: UploadFile):
    processor = NewProcessor()
    result = processor.process(file.filename)
    return ProcessingResponse(**result)
```

## API Documentation

Visit http://localhost:8001/docs for interactive API documentation (Swagger UI).

## License

Part of the Aura PKM project.
