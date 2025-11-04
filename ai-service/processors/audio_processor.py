"""
Audio/Video Processor - Transcription and analysis
Supports: Audio files (mp3, wav, m4a, etc.), Video files (mp4, webm), YouTube links
"""

import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
import asyncio

from .base import BaseProcessor, ProcessingResult, ProcessorError, ProcessorProvider
from services.llm_service import get_llm_service
from config import settings


class AudioProcessor(BaseProcessor):
    """
    Audio/Video processor with provider abstraction

    Current implementation:
    - Audio transcription: OpenAI Whisper API (most accurate)
    - Video: Extract audio � Whisper API
    - YouTube: youtube-transcript-api + metadata
    - Analysis: Gemini Flash (free tier)

    Future support:
    - Local Whisper models
    - Local LLM for analysis
    """

    SUPPORTED_AUDIO_FORMATS = ['mp3', 'wav', 'm4a', 'aac', 'ogg', 'flac', 'wma']
    SUPPORTED_VIDEO_FORMATS = ['mp4', 'webm', 'avi', 'mov', 'mkv', 'flv']

    def __init__(self, provider: ProcessorProvider = ProcessorProvider.OPENAI_API):
        """Initialize audio processor"""
        super().__init__(provider)
        self.llm = get_llm_service()  # For analysis

    def get_supported_formats(self) -> List[str]:
        """Get all supported audio and video formats"""
        return self.SUPPORTED_AUDIO_FORMATS + self.SUPPORTED_VIDEO_FORMATS

    def validate_file(self, file_path: str) -> bool:
        """Validate audio/video file exists and has supported format"""
        path = Path(file_path)
        if not path.exists():
            return False

        extension = path.suffix.lstrip('.').lower()
        return extension in self.get_supported_formats()

    async def process(
        self,
        file_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """
        Process audio or video file

        Args:
            file_path: Path to audio/video file OR YouTube URL
            options: Optional parameters:
                - language: Language code for transcription
                - extract_speakers: Whether to attempt speaker diarization
                - youtube_url: If this is a YouTube video

        Returns:
            ProcessingResult with transcription and analysis
        """
        try:
            options = options or {}

            # Check if it's a YouTube URL
            if self._is_youtube_url(file_path):
                return await self._process_youtube(file_path, options)

            # Validate file
            if not self.validate_file(file_path):
                raise ProcessorError(f"Invalid or unsupported file: {file_path}")

            # Check if it's a video file
            path = Path(file_path)
            extension = path.suffix.lstrip('.').lower()

            if extension in self.SUPPORTED_VIDEO_FORMATS:
                # Extract audio from video
                audio_path = await self._extract_audio_from_video(file_path)
                transcription = await self._transcribe_audio(audio_path, options)

                # Clean up temporary audio file
                if audio_path != file_path:
                    try:
                        os.remove(audio_path)
                    except:
                        pass
            else:
                # Direct audio transcription
                transcription = await self._transcribe_audio(file_path, options)

            # Analyze content with LLM
            analysis = await self.llm.analyze_content(transcription, "transcription")

            return ProcessingResult(
                success=True,
                raw_text=transcription,
                summary=analysis.get("summary"),
                key_points=self._extract_key_points(analysis.get("summary", "")),
                extracted_tasks=analysis.get("tasks", []),
                metadata={
                    "provider": self.provider.value,
                    "file_type": extension,
                    "word_count": len(transcription.split()),
                    "character_count": len(transcription),
                    "is_resource": analysis.get("is_resource", False),
                    "suggested_projects": analysis.get("projects", []),
                    "suggested_areas": analysis.get("areas", []),
                },
                confidence_score=analysis.get("confidence", 0.85),
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                error=f"Audio processing failed: {str(e)}"
            )

    def _is_youtube_url(self, url: str) -> bool:
        """Check if string is a YouTube URL"""
        youtube_patterns = [
            r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/',
            r'youtube\.com/watch\?v=',
            r'youtu\.be/',
        ]
        return any(re.search(pattern, url) for pattern in youtube_patterns)

    async def _process_youtube(
        self,
        url: str,
        options: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Process YouTube video

        Uses youtube-transcript-api (free) to get transcript
        Falls back to audio extraction if transcript unavailable
        """
        try:
            # Try to get existing transcript first (free!)
            from youtube_transcript_api import YouTubeTranscriptApi
            import re

            # Extract video ID
            video_id = self._extract_youtube_video_id(url)
            if not video_id:
                raise ProcessorError("Could not extract YouTube video ID")

            # Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcription = " ".join([entry['text'] for entry in transcript_list])

            # Get video metadata (free - just HTTP request)
            metadata = await self._get_youtube_metadata(video_id)

            # Analyze with LLM
            analysis = await self.llm.analyze_content(transcription, "youtube video")

            return ProcessingResult(
                success=True,
                raw_text=transcription,
                summary=analysis.get("summary"),
                key_points=self._extract_key_points(analysis.get("summary", "")),
                extracted_tasks=analysis.get("tasks", []),
                metadata={
                    "provider": "youtube_transcript_api",
                    "video_id": video_id,
                    "url": url,
                    "title": metadata.get("title"),
                    "duration": metadata.get("duration"),
                    "word_count": len(transcription.split()),
                    "is_resource": analysis.get("is_resource", False),
                    "suggested_projects": analysis.get("projects", []),
                    "suggested_areas": analysis.get("areas", []),
                },
                confidence_score=analysis.get("confidence", 0.85),
            )

        except Exception as e:
            # Transcript not available - would need to download and transcribe
            # For free tier, we'll just return error
            return ProcessingResult(
                success=False,
                error=f"YouTube processing failed: {str(e)}. Transcript may not be available."
            )

    def _extract_youtube_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    async def _get_youtube_metadata(self, video_id: str) -> Dict[str, Any]:
        """Get YouTube video metadata (free - no API key needed for basic info)"""
        # This would use yt-dlp or similar to get metadata
        # For now, return basic info
        return {
            "video_id": video_id,
            "title": f"YouTube Video {video_id}",
            "duration": None,
        }

    async def _extract_audio_from_video(self, video_path: str) -> str:
        """
        Extract audio track from video file

        Returns:
            Path to extracted audio file
        """
        try:
            from moviepy.editor import VideoFileClip
            import tempfile

            # Create temp file for audio
            temp_audio = tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.mp3',
                dir=settings.upload_dir
            )
            temp_audio_path = temp_audio.name
            temp_audio.close()

            # Extract audio
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(
                temp_audio_path,
                codec='mp3',
                verbose=False,
                logger=None
            )
            video.close()

            return temp_audio_path

        except ImportError:
            # moviepy not available, return original path
            # Will fail at transcription if it's a video file
            raise ProcessorError(
                "moviepy not installed. Cannot extract audio from video. "
                "Install with: pip install moviepy"
            )

    async def _transcribe_audio(
        self,
        audio_path: str,
        options: Dict[str, Any]
    ) -> str:
        """
        Transcribe audio file using configured provider

        Current implementation: OpenAI Whisper API (most accurate)
        Future: Support for local Whisper models
        """
        if self.provider == ProcessorProvider.OPENAI_API:
            return await self._transcribe_with_openai_whisper(audio_path, options)
        elif self.provider == ProcessorProvider.LOCAL_WHISPER:
            return await self._transcribe_with_local_whisper(audio_path, options)
        else:
            raise ProcessorError(f"Unsupported provider for audio: {self.provider}")

    async def _transcribe_with_openai_whisper(
        self,
        audio_path: str,
        options: Dict[str, Any]
    ) -> str:
        """Transcribe using OpenAI Whisper API"""
        try:
            from openai import OpenAI

            if not settings.openai_api_key:
                raise ProcessorError("OPENAI_API_KEY not set for Whisper transcription")

            client = OpenAI(api_key=settings.openai_api_key)

            with open(audio_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=options.get('language'),  # Optional: en, es, fr, etc.
                )

            return transcript.text

        except Exception as e:
            raise ProcessorError(f"OpenAI Whisper transcription failed: {str(e)}")

    async def _transcribe_with_local_whisper(
        self,
        audio_path: str,
        options: Dict[str, Any]
    ) -> str:
        """
        Transcribe using local Whisper model

        Future implementation for offline processing
        """
        raise NotImplementedError("Local Whisper not yet implemented")

    def _extract_key_points(self, summary: str) -> List[str]:
        """Extract key points from summary text"""
        # Simple extraction based on sentences
        sentences = [s.strip() for s in summary.split('.') if s.strip()]
        return sentences[:5]  # Return up to 5 key points
