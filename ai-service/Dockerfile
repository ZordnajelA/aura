FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download Whisper model (optional - can be done at runtime)
# RUN python -c "import whisper; whisper.load_model('base')"

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /app/uploads /app/models

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
