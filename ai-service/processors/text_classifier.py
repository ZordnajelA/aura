"""
Text Classifier - Classify and analyze text inputs
Determines content type, priority, and suggests PARA organization
"""

from typing import Dict, Any, List, Optional

from .base import BaseProcessor, ProcessingResult, ProcessorError, ProcessorProvider
from services.llm_service import get_llm_service
from config import settings


class TextClassifier(BaseProcessor):
    """
    Text content classifier and analyzer

    Classifies text into categories:
    - Task (actionable item)
    - Log entry (journal, reflection)
    - Thought/Idea
    - Meeting note
    - Invoice/Financial
    - Email/Message
    - Reference material

    Also suggests PARA organization and priority
    """

    SUPPORTED_FORMATS = ['text']

    def __init__(self, provider: ProcessorProvider = ProcessorProvider.GEMINI_API):
        """Initialize text classifier"""
        super().__init__(provider)
        self.llm = get_llm_service()

    def get_supported_formats(self) -> List[str]:
        """Get supported formats"""
        return self.SUPPORTED_FORMATS

    def validate_file(self, file_path: str) -> bool:
        """Not applicable for text classification"""
        return True

    async def process(
        self,
        file_path: str,  # In this case, file_path contains the text to classify
        options: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """
        Classify and analyze text content

        Args:
            file_path: The text content to classify (not actually a file path)
            options: Optional parameters:
                - context: Additional context about the text
                - user_areas: List of user's existing areas
                - user_projects: List of user's existing projects

        Returns:
            ProcessingResult with classification and suggestions
        """
        try:
            options = options or {}
            text = file_path  # For text classification, "file_path" is the text content

            if not text or not text.strip():
                raise ProcessorError("Empty text provided for classification")

            # Classify the text
            classification = await self._classify_text(text, options)

            # Generate summary
            summary = classification.get("summary", text[:200])

            # Extract tasks if it's actionable
            tasks = classification.get("tasks", [])
            if classification.get("is_actionable"):
                tasks = await self.llm.extract_tasks(text)

            # Build metadata
            metadata = {
                "provider": self.provider.value,
                "classification_type": classification.get("type"),
                "is_actionable": classification.get("is_actionable", False),
                "priority": classification.get("priority"),
                "suggested_area": classification.get("suggested_area"),
                "suggested_project": classification.get("suggested_project"),
                "is_resource": classification.get("is_resource", False),
                "requires_followup": classification.get("requires_followup", False),
                "sentiment": classification.get("sentiment"),
            }

            # Extract invoice details if classified as invoice
            if classification.get("type") == "invoice":
                invoice_details = await self.llm.extract_invoice_details(text)
                metadata["invoice_details"] = invoice_details

            return ProcessingResult(
                success=True,
                raw_text=text,
                summary=summary,
                key_points=classification.get("key_points", []),
                extracted_tasks=tasks,
                metadata=metadata,
                confidence_score=classification.get("confidence", 0.8),
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                error=f"Text classification failed: {str(e)}"
            )

    async def _classify_text(
        self,
        text: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify text using LLM

        Args:
            text: Text to classify
            options: Classification options

        Returns:
            Dictionary with classification results
        """
        try:
            # Build context
            context_parts = []
            if options.get('context'):
                context_parts.append(f"Context: {options['context']}")

            if options.get('user_areas'):
                context_parts.append(f"User's Areas: {', '.join(options['user_areas'])}")

            if options.get('user_projects'):
                context_parts.append(f"User's Projects: {', '.join(options['user_projects'])}")

            context = "\n".join(context_parts) if context_parts else ""

            # Create classification prompt
            prompt = f"""Analyze and classify the following text content.

IMPORTANT: Respond in English only, regardless of the input language. All summaries, key points, tasks, and suggestions must be in English.

Text to classify:
{text}

{context}

Provide a detailed classification with the following information:

1. **Type**: What kind of content is this?
   - task: A specific actionable item with clear outcome
   - log_entry: A journal entry, daily log, or personal reflection
   - thought: An idea, observation, or brainstorm
   - meeting_note: Notes from a meeting or discussion
   - invoice: Financial document or receipt
   - email: Email or message correspondence
   - reference: Reference material, article, or resource
   - other: Doesn't fit above categories

2. **Summary**: A concise 1-2 sentence summary

3. **Key Points**: 2-5 main points or takeaways

4. **Is Actionable**: Does this require any action? (true/false)

5. **Priority**: If actionable, what's the priority?
   - urgent: Time-sensitive, critical
   - high: Important, should do soon
   - medium: Normal priority
   - low: Nice to have, can wait
   - null: Not actionable

6. **Tasks**: If actionable, list specific action items

7. **PARA Suggestions**:
   - suggested_area: Which Area does this belong to? (e.g., Work, Health, Finance, Personal Development)
   - suggested_project: Is this related to a specific project?
   - is_resource: Should this be saved as a reference resource?

8. **Additional Flags**:
   - requires_followup: Does this need follow-up later?
   - sentiment: Overall tone (positive, neutral, negative, mixed)

9. **Confidence**: How confident is this classification? (0.0 to 1.0)

Respond ONLY in JSON format:
{{
    "type": "task|log_entry|thought|meeting_note|invoice|email|reference|other",
    "summary": "Brief summary of content",
    "key_points": ["point 1", "point 2"],
    "is_actionable": true|false,
    "priority": "urgent|high|medium|low|null",
    "tasks": ["task 1", "task 2"],
    "suggested_area": "Area name or null",
    "suggested_project": "Project name or null",
    "is_resource": true|false,
    "requires_followup": true|false,
    "sentiment": "positive|neutral|negative|mixed",
    "confidence": 0.0-1.0
}}"""

            # Generate classification
            response = await self.llm.generate(prompt, max_tokens=1000, temperature=0.2)

            # Parse JSON response
            import json
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            result = json.loads(response)
            return result

        except Exception as e:
            print(f"Classification error: {e}")
            # Fallback basic classification
            return {
                "type": "other",
                "summary": text[:200],
                "key_points": [],
                "is_actionable": False,
                "priority": None,
                "tasks": [],
                "suggested_area": None,
                "suggested_project": None,
                "is_resource": False,
                "requires_followup": False,
                "sentiment": "neutral",
                "confidence": 0.5,
                "error": str(e),
            }
