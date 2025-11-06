"""
LLM Service - Multi-provider support for AI text generation
Supports: Google Gemini (primary), OpenAI GPT, Anthropic Claude
"""

from typing import Dict, Any, Optional
import os
from config import settings
from services.rate_limiter import get_rate_limiter


class LLMService:
    """
    Unified interface for multiple LLM providers
    Automatically uses the configured default provider
    """

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize LLM service with specified provider

        Args:
            provider: LLM provider (gemini, openai, anthropic).
                     If None, uses DEFAULT_LLM_PROVIDER from settings
        """
        self.provider = provider or settings.default_llm_provider
        self._client = None
        self._rate_limiter = get_rate_limiter(self.provider)
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate LLM client based on provider"""
        if self.provider == "gemini":
            self._initialize_gemini()
        elif self.provider == "openai":
            self._initialize_openai()
        elif self.provider == "anthropic":
            self._initialize_anthropic()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _initialize_gemini(self):
        """Initialize Google Gemini client"""
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not set in environment")

        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.google_api_key)
            self._client = genai.GenerativeModel(settings.gemini_model)
            print(f"✓ Gemini initialized with model: {settings.gemini_model}")
        except ImportError:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")

    def _initialize_openai(self):
        """Initialize OpenAI client"""
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=settings.openai_api_key)
            print(f"✓ OpenAI initialized with model: {settings.openai_model}")
        except ImportError:
            raise ImportError("openai not installed. Run: pip install openai")

    def _initialize_anthropic(self):
        """Initialize Anthropic Claude client"""
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")

        try:
            from anthropic import Anthropic
            self._client = Anthropic(api_key=settings.anthropic_api_key)
            print(f"✓ Anthropic initialized with model: {settings.anthropic_model}")
        except ImportError:
            raise ImportError("anthropic not installed. Run: pip install anthropic")

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text using the configured LLM provider

        Args:
            prompt: Input prompt for the LLM
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text response
        """
        # Apply rate limiting
        await self._rate_limiter.acquire()

        if self.provider == "gemini":
            return self._generate_gemini(prompt, max_tokens, temperature, **kwargs)
        elif self.provider == "openai":
            return self._generate_openai(prompt, max_tokens, temperature, **kwargs)
        elif self.provider == "anthropic":
            return self._generate_anthropic(prompt, max_tokens, temperature, **kwargs)

    def _generate_gemini(self, prompt: str, max_tokens: int, temperature: float, **kwargs) -> str:
        """Generate using Google Gemini"""
        response = self._client.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature,
                **kwargs
            }
        )
        return response.text

    def _generate_openai(self, prompt: str, max_tokens: int, temperature: float, **kwargs) -> str:
        """Generate using OpenAI GPT"""
        response = self._client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].message.content

    def _generate_anthropic(self, prompt: str, max_tokens: int, temperature: float, **kwargs) -> str:
        """Generate using Anthropic Claude"""
        response = self._client.messages.create(
            model=settings.anthropic_model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.content[0].text

    async def analyze_content(self, content: str, content_type: str) -> Dict[str, Any]:
        """
        Analyze content and generate PARA suggestions

        Args:
            content: Text content to analyze
            content_type: Type of content (text, transcription, ocr, etc.)

        Returns:
            Dictionary with analysis results and PARA suggestions
        """
        prompt = f"""Analyze the following {content_type} content and provide:

IMPORTANT: Respond in English only, regardless of the input language. All output must be in English.

1. A concise summary (~500 characters)
2. Extracted tasks or action items (if any)
3. Relevant project suggestions
4. Relevant area suggestions (ongoing responsibilities)
5. Whether this should be a resource (reference material)

Content:
{content}

Respond in JSON format:
{{
    "summary": "...",
    "tasks": ["task1", "task2"],
    "projects": ["project name if this seems like a project-related item"],
    "areas": ["area name like Health, Finance, etc."],
    "is_resource": true/false,
    "confidence": 0.0-1.0
}}"""

        try:
            response = await self.generate(prompt, max_tokens=1000, temperature=0.3)

            # Parse JSON response
            import json
            # Try to extract JSON from response (some models wrap it in markdown)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            result = json.loads(response)
            return result

        except Exception as e:
            print(f"Error analyzing content: {e}")
            return {
                "summary": content[:500],
                "tasks": [],
                "projects": [],
                "areas": [],
                "is_resource": False,
                "confidence": 0.0,
                "error": str(e)
            }

    async def summarize(self, content: str, max_length: int = 500) -> str:
        """
        Generate a concise summary of content

        Args:
            content: Text to summarize
            max_length: Maximum character length of summary

        Returns:
            Summary text
        """
        prompt = f"""Provide a concise summary of the following content in approximately {max_length} characters.
Focus on the main points and key information.

IMPORTANT: Respond in English only, regardless of the input language.

Content:
{content}

Summary (in English):"""

        return await self.generate(prompt, max_tokens=200, temperature=0.5)

    async def extract_tasks(self, content: str) -> list[str]:
        """
        Extract actionable tasks from content

        Args:
            content: Text to analyze

        Returns:
            List of extracted tasks
        """
        prompt = f"""Extract all actionable tasks or to-do items from the following content.
Return ONLY a JSON array of task strings, nothing else.

IMPORTANT: All tasks must be in English, regardless of the input language.

Content:
{content}

Tasks (JSON array in English):"""

        try:
            response = await self.generate(prompt, max_tokens=300, temperature=0.3)

            # Try to parse JSON array
            import json
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            tasks = json.loads(response)
            return tasks if isinstance(tasks, list) else []

        except Exception as e:
            print(f"Error extracting tasks: {e}")
            return []


# Singleton instance
_llm_service = None


def get_llm_service(provider: Optional[str] = None) -> LLMService:
    """
    Get or create LLM service instance

    Args:
        provider: Optional specific provider to use

    Returns:
        LLMService instance
    """
    global _llm_service
    if _llm_service is None or provider is not None:
        _llm_service = LLMService(provider)
    return _llm_service
