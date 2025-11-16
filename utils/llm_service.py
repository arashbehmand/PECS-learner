import json
import logging
import os
import re
from typing import Dict, List, Optional

import litellm
import yaml
from litellm import completion
from openai import OpenAI

from nicegui_app.config import LLM_MODEL_DEFAULT, LLM_MODEL_FAST, LLM_MODEL_QUALITY

# Setup logging
logger = logging.getLogger(__name__)

# Configure LiteLLM
litellm.drop_params = True  # Drop unsupported params instead of erroring
litellm.set_verbose = os.getenv("LITELLM_VERBOSE", "false").lower() == "true"


def extract_json_from_markdown(content: str) -> str:
    """Extract JSON from markdown code blocks if present, otherwise return as-is."""
    # Try to find JSON in markdown code blocks (```json ... ``` or ``` ... ```)
    patterns = [
        r"```json\s*\n(.*?)\n```",  # ```json ... ```
        r"```\s*\n(.*?)\n```",  # ``` ... ```
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()

    # If no code block found, return original content
    return content.strip()


class LLMService:
    def __init__(self):
        """Initialize the LLM service with API key from environment or secrets."""
        # Load prompts from YAML
        with open("utils/prompts.yaml", "r", encoding="utf-8") as f:
            self.prompts = yaml.safe_load(f)

        # Initialize client attribute so tests can rely on its presence
        self.client: Optional[OpenAI] = None

        # Check if API key is available (LiteLLM reads from env automatically)
        self.api_key = (
            os.getenv("OPENAI_API_KEY")
            or os.getenv("ANTHROPIC_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("LLM client initialized via OpenAI SDK")
        else:
            logger.warning(
                "No API key found. LLM features will be unavailable. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY."
            )

        # Configure Langfuse for observability (if available)
        langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

        if langfuse_public_key and langfuse_secret_key:
            try:
                # Enable Langfuse integration with LiteLLM
                litellm.success_callback = ["langfuse"]
                litellm.failure_callback = ["langfuse"]
                os.environ.setdefault("LANGFUSE_PUBLIC_KEY", langfuse_public_key)
                os.environ.setdefault("LANGFUSE_SECRET_KEY", langfuse_secret_key)
                os.environ.setdefault("LANGFUSE_HOST", langfuse_host)
                logger.info(
                    "LLM service initialized with Langfuse observability via LiteLLM"
                )
            except Exception as e:
                logger.warning(
                    "Langfuse integration failed (%s). Continuing without observability.",
                    e,
                )
        else:
            logger.info(
                "LLM service initialized without observability (set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY for tracking)"
            )

        # Configure models from config (configurable via environment variables)
        self.model = LLM_MODEL_DEFAULT  # Default model for general tasks
        self.model_fast = LLM_MODEL_FAST  # Fast model for quick tasks (rolling context)
        self.model_quality = (
            LLM_MODEL_QUALITY  # Quality model for important tasks (study notes)
        )

    def is_available(self) -> bool:
        """Check if LLM service is available.

        Availability is determined by having an initialized client and loaded prompts.
        This makes behavior deterministic for tests which mock/assign the client directly.
        """
        return self.client is not None and self.prompts is not None

    def _get_prompt(self, module: str, prompt_type: str) -> Optional[Dict[str, str]]:
        """Get prompt template from YAML configuration."""
        try:
            return self.prompts[module][prompt_type]
        except KeyError:
            logger.error(f"Prompt template not found: {module}.{prompt_type}")
            return None

    def _make_llm_call(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Make a call to the LLM API.

        Prefer using an initialized client (e.g. OpenAI SDK) when available so tests
        that mock client.chat.completions.create are exercised. Fall back to litellm.completion.
        """
        if not self.is_available():
            logger.warning(
                "LLM service is not available. Please check your API key configuration."
            )
            return None

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error making LLM call: {str(e)}")
            return None

    def make_llm_call(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Public wrapper for making LLM calls."""
        return self._make_llm_call(system_prompt, user_prompt)

    # Prime Module Methods
    def analyze_section_understanding(
        self, chunk_text: str, student_response: str
    ) -> Optional[str]:
        """Analyze student's initial understanding of a section."""
        prompt = self._get_prompt("prime_module", "section_analysis")
        if not prompt:
            return None

        user_prompt = prompt["user"].format(
            chunk_text=chunk_text, student_response=student_response
        )
        return self._make_llm_call(prompt["system"], user_prompt)

    def analyze_questions(
        self, chunk_text: str, student_questions: str
    ) -> Optional[str]:
        """Analyze student's questions about a section."""
        prompt = self._get_prompt("prime_module", "question_analysis")
        if not prompt:
            return None

        user_prompt = prompt["user"].format(
            chunk_text=chunk_text, student_questions=student_questions
        )
        return self._make_llm_call(prompt["system"], user_prompt)

    # Engage Module Methods
    def analyze_explanation(
        self, chunk_text: str, student_explanation: str
    ) -> Optional[str]:
        """Analyze student's explanation of a section."""
        prompt = self._get_prompt("engage_module", "explanation_analysis")
        if not prompt:
            return None

        user_prompt = prompt["user"].format(
            chunk_text=chunk_text, student_explanation=student_explanation
        )
        return self._make_llm_call(prompt["system"], user_prompt)

    def analyze_analogy(self, chunk_text: str, student_analogy: str) -> Optional[str]:
        """Analyze student's analogy for a concept."""
        prompt = self._get_prompt("engage_module", "analogy_analysis")
        if not prompt:
            return None

        user_prompt = prompt["user"].format(
            chunk_text=chunk_text, student_analogy=student_analogy
        )
        return self._make_llm_call(prompt["system"], user_prompt)

    # Challenge Module Methods
    def analyze_critical_thinking(
        self, chunk_text: str, student_analysis: str
    ) -> Optional[str]:
        """Analyze student's critical thinking about a section."""
        prompt = self._get_prompt("challenge_module", "critical_analysis")
        if not prompt:
            return None

        user_prompt = prompt["user"].format(
            chunk_text=chunk_text, student_analysis=student_analysis
        )
        return self._make_llm_call(prompt["system"], user_prompt)

    def analyze_connections(
        self, chunk_text: str, student_connections: str
    ) -> Optional[str]:
        """Analyze student's connections between concepts."""
        prompt = self._get_prompt("challenge_module", "connection_analysis")
        if not prompt:
            return None

        user_prompt = prompt["user"].format(
            chunk_text=chunk_text, student_connections=student_connections
        )
        return self._make_llm_call(prompt["system"], user_prompt)

    # Solidify Module Methods
    def analyze_flashcards(
        self, chunk_text: str, student_flashcards: List[Dict[str, str]]
    ) -> Optional[str]:
        """Analyze student's flashcards for a section."""
        prompt = self._get_prompt("solidify_module", "flashcard_analysis")
        if not prompt:
            return None

        user_prompt = prompt["user"].format(
            chunk_text=chunk_text,
            student_flashcards=json.dumps(student_flashcards, indent=2),
        )
        return self._make_llm_call(prompt["system"], user_prompt)

    def analyze_application(
        self, chunk_text: str, student_application: str
    ) -> Optional[str]:
        """Analyze student's application of concepts."""
        prompt = self._get_prompt("solidify_module", "application_analysis")
        if not prompt:
            return None

        user_prompt = prompt["user"].format(
            chunk_text=chunk_text, student_application=student_application
        )
        return self._make_llm_call(prompt["system"], user_prompt)

    def get_simplicity_feedback(self, explanation: str) -> Optional[str]:
        """Get feedback on explanation simplicity and clarity."""
        return self.analyze_explanation("", explanation)  # Reuse explanation analysis

    def suggest_flashcards_with_context(
        self, formatted_context: str
    ) -> Optional[List[Dict[str, str]]]:
        """Suggest flashcard Q/A pairs based on formatted learning context.

        Uses pre-formatted context from build_learning_context() and
        format_context_for_flashcards().

        Args:
            formatted_context: Pre-formatted string with all learning context

        Returns:
            List of flashcard dicts with 'question' and 'answer' keys
        """
        if not self.is_available():
            logger.warning(
                "LLM service is not available. Please check your API key configuration."
            )
            return None

        try:
            prompt = f"""{formatted_context}

Based on the student's learning journey above, suggest 2-3 high-quality flashcard Q/A pairs.

Requirements:
1. Question should be clear and test understanding
2. Answer should be concise but complete
3. Focus on key concepts and relationships
4. Avoid trivial or obvious questions
5. If existing flashcards are listed above, generate DIFFERENT cards on new aspects

Return ONLY a JSON array of objects, each with 'question' and 'answer' fields.
Example: [{{"question": "...", "answer": "..."}}, {{"question": "...", "answer": "..."}}]"""

            logger.debug(f"Flashcard generation prompt length: {len(prompt)} chars")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a learning assistant creating effective flashcards. Always return valid JSON array.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            content = response.choices[0].message.content
            logger.debug(f"Raw LLM response: {content[:200]}...")

            # Extract JSON from potential markdown wrapper
            json_str = extract_json_from_markdown(content)

            try:
                qa_pairs = json.loads(json_str)
                if isinstance(qa_pairs, list):
                    logger.info(f"Successfully generated {len(qa_pairs)} flashcards")
                    return qa_pairs[:3]  # Return at most 3 pairs

                logger.error(f"Flashcard response is not a list: {type(qa_pairs)}")
                return None
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse flashcard suggestions as JSON: {e}")
                logger.error(f"Attempted to parse: {json_str[:200]}")
                return None

        except Exception as e:
            logger.error(
                f"Error generating flashcard suggestions: {str(e)}", exc_info=True
            )
            return None

    def suggest_flashcards(
        self,
        chunk_text: str,
        user_explanation: str,
        user_challenges: str,
        existing_cards: List[Dict[str, str]] = None,
    ) -> Optional[List[Dict[str, str]]]:
        """Suggest flashcard Q/A pairs based on the material and user's understanding."""
        if not self.is_available():
            logger.warning(
                "LLM service is not available. Please check your API key configuration."
            )
            return None

        try:
            # Build existing cards context if provided
            existing_context = ""
            if existing_cards and len(existing_cards) > 0:
                existing_context = (
                    "\n\nPreviously suggested flashcards (DO NOT duplicate these):\n"
                )
                for i, card in enumerate(existing_cards, 1):
                    existing_context += (
                        f"{i}. Q: {card['question']}\n   A: {card['answer']}\n"
                    )
                existing_context += (
                    "\nGenerate NEW flashcards on different aspects of the material."
                )

            prompt = f"""Based on the following learning material and the user's understanding,
            suggest 2-3 high-quality flashcard Q/A pairs that would help reinforce key concepts.

            Original Material:
            {chunk_text[:1500]}...

            User's Explanation:
            {user_explanation}

            User's Challenges/Questions:
            {user_challenges}
            {existing_context}

            For each flashcard:
            1. Question should be clear and test understanding
            2. Answer should be concise but complete
            3. Focus on key concepts and relationships
            4. Avoid trivial or obvious questions
            5. DO NOT duplicate existing flashcards if provided above

            Return the response as a JSON array of objects, each with 'question' and 'answer' fields."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful learning assistant focused on creating effective flashcards. Always return valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            content = response.choices[0].message.content
            logger.debug(f"Raw LLM response: {content}")

            # Extract JSON from potential markdown wrapper
            json_str = extract_json_from_markdown(content)
            logger.debug(f"Extracted JSON: {json_str}")

            try:
                qa_pairs = json.loads(json_str)
                if isinstance(qa_pairs, list):
                    return qa_pairs[:3]  # Return at most 3 pairs

                logger.error(f"Flashcard response is not a list: {type(qa_pairs)}")
                return None
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse flashcard suggestions as JSON: {e}")
                logger.error(f"Attempted to parse: {json_str[:200]}")
                return None

        except Exception as e:
            logger.error(f"Error generating flashcard suggestions: {str(e)}")
            return None

    # Rolling Context Methods
    def generate_rolling_summary(
        self,
        previous_summary: str,
        current_content: str,
        section_title: str,
    ) -> Optional[str]:
        """
        Generate a rolling summary that integrates current section with previous sections.

        This implements the "rolling window context" from the document summarizer.
        Uses fast model for efficiency.

        Args:
            previous_summary: Summary of all previous sections
            current_content: Content of current section
            section_title: Title of current section

        Returns:
            Updated rolling summary, or None if error
        """
        prompt = self._get_prompt("rolling_context_module", "generate_summary")
        if not prompt:
            logger.error("Rolling summary prompt not found")
            return None

        user_prompt = prompt["user"].format(
            previous_summary=previous_summary or "This is the first section.",
            current_content=current_content,
            section_title=section_title,
        )

        try:
            response = completion(
                model=self.model_fast,  # Use fast model for rolling context
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating rolling summary: {e}", exc_info=True)
            return None

    # Study Notes Methods
    def generate_study_notes(
        self,
        rolling_summary: str,
        section_title: str,
        section_content: str,
        pecs_summary: str = "",
    ) -> Optional[str]:
        """
        Generate study notes for a section.

        Focuses on: diagrams, connections, definitions, key concepts (not summaries).
        Uses quality model for better output.

        Args:
            rolling_summary: Context from previous sections
            section_title: Title of current section
            section_content: Content of current section
            pecs_summary: Optional summary of student's learning journey

        Returns:
            Generated study notes in markdown format, or None if error
        """
        prompt = self._get_prompt("study_notes_module", "generate_section_notes")
        if not prompt:
            return None

        user_prompt = prompt["user"].format(
            rolling_summary=rolling_summary or "This is the first section.",
            section_title=section_title,
            section_content=section_content,
            pecs_summary=pecs_summary or "No student learning data available yet.",
        )

        try:
            response = completion(
                model=self.model_quality,  # Use quality model for study notes
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating study notes: {e}", exc_info=True)
            return None

    def combine_study_notes(self, all_section_notes: List[str]) -> Optional[str]:
        """
        Combine individual section notes into a cohesive study guide.

        This is the "reduce" phase from the document summarizer.
        Uses quality model for better synthesis.

        Args:
            all_section_notes: List of study notes from all sections

        Returns:
            Combined study guide, or None if error
        """
        prompt = self._get_prompt("study_notes_module", "combine_section_notes")
        if not prompt:
            return None

        # Format all section notes with separators
        formatted_notes = "\n\n" + "=" * 60 + "\n\n".join(all_section_notes)

        user_prompt = prompt["user"].format(all_section_notes=formatted_notes)

        try:
            response = completion(
                model=self.model_quality,  # Use quality model
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error combining study notes: {e}", exc_info=True)
            return None

    def refine_study_notes(self, draft_notes: str) -> Optional[str]:
        """
        Refine and polish study notes for clarity and effectiveness.

        This is the "consistency" phase from the document summarizer.
        Uses quality model for final polish.

        Args:
            draft_notes: Draft study notes to refine

        Returns:
            Refined study notes, or None if error
        """
        prompt = self._get_prompt("study_notes_module", "refine_study_notes")
        if not prompt:
            return None

        user_prompt = prompt["user"].format(draft_notes=draft_notes)

        try:
            response = completion(
                model=self.model_quality,  # Use quality model
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error refining study notes: {e}", exc_info=True)
            return None
