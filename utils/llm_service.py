import os
import json
import yaml
import re
from typing import Optional, Dict, Any, List
import logging
from openai import OpenAI
from openai.types.chat import ChatCompletion

# Setup logging
logger = logging.getLogger(__name__)

# Try to import Langfuse (optional)
try:
    from langfuse.openai import OpenAI as LangfuseOpenAI
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    logger.info("Langfuse not available. Install 'langfuse' for LLM observability.")

def extract_json_from_markdown(content: str) -> str:
    """Extract JSON from markdown code blocks if present, otherwise return as-is."""
    # Try to find JSON in markdown code blocks (```json ... ``` or ``` ... ```)
    patterns = [
        r'```json\s*\n(.*?)\n```',  # ```json ... ```
        r'```\s*\n(.*?)\n```',       # ``` ... ```
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
        try:
            # Load prompts from YAML
            with open('utils/prompts.yaml', 'r') as f:
                self.prompts = yaml.safe_load(f)

            # Try to get the API key from multiple sources
            self.api_key = None

            # 1. Try environment variable
            self.api_key = os.getenv('OPENAI_API_KEY')

            # 2. Try Streamlit secrets if available (for backward compatibility)
            if not self.api_key:
                try:
                    import streamlit as st
                    if hasattr(st, 'secrets') and "llm" in st.secrets:
                        self.api_key = st.secrets["llm"]["openai_api_key"]
                except (ImportError, FileNotFoundError, KeyError):
                    pass

            # Initialize client if we have an API key
            if self.api_key:
                # Try to use Langfuse for observability if available and configured
                if LANGFUSE_AVAILABLE:
                    langfuse_public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
                    langfuse_secret_key = os.getenv('LANGFUSE_SECRET_KEY')
                    langfuse_host = os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')

                    if langfuse_public_key and langfuse_secret_key:
                        try:
                            self.client = LangfuseOpenAI(
                                api_key=self.api_key,
                                langfuse_public_key=langfuse_public_key,
                                langfuse_secret_key=langfuse_secret_key,
                                langfuse_host=langfuse_host
                            )
                            logger.info("LLM service initialized with Langfuse observability")
                        except Exception as e:
                            logger.warning(f"Failed to initialize Langfuse: {e}. Falling back to standard OpenAI client.")
                            self.client = OpenAI(api_key=self.api_key)
                            logger.info("LLM service initialized without observability")
                    else:
                        self.client = OpenAI(api_key=self.api_key)
                        logger.info("LLM service initialized without observability (set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY for tracking)")
                else:
                    self.client = OpenAI(api_key=self.api_key)
                    logger.info("LLM service initialized without observability")
            else:
                self.client = None
                logger.warning("No OpenAI API key found. LLM features will be unavailable.")

            self.model = "gpt-3.5-turbo"  # Default to a cost-effective model

        except Exception as e:
            logger.error(f"Error initializing LLM service: {str(e)}")
            self.client = None
            self.api_key = None
            self.prompts = None

    def is_available(self) -> bool:
        """Check if LLM service is available (API key configured)."""
        return self.client is not None and self.prompts is not None

    def _get_prompt(self, module: str, prompt_type: str) -> Optional[Dict[str, str]]:
        """Get prompt template from YAML configuration."""
        try:
            return self.prompts[module][prompt_type]
        except KeyError:
            logger.error(f"Prompt template not found: {module}.{prompt_type}")
            return None

    def _make_llm_call(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Make a call to the LLM API."""
        if not self.is_available():
            logger.warning("LLM service is not available. Please check your API key configuration.")
            return None

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error making LLM call: {str(e)}")
            return None

    # Prime Module Methods
    def analyze_section_understanding(self, chunk_text: str, student_response: str) -> Optional[str]:
        """Analyze student's initial understanding of a section."""
        prompt = self._get_prompt('prime_module', 'section_analysis')
        if not prompt:
            return None
        
        user_prompt = prompt['user'].format(
            chunk_text=chunk_text,
            student_response=student_response
        )
        return self._make_llm_call(prompt['system'], user_prompt)

    def analyze_questions(self, chunk_text: str, student_questions: str) -> Optional[str]:
        """Analyze student's questions about a section."""
        prompt = self._get_prompt('prime_module', 'question_analysis')
        if not prompt:
            return None
        
        user_prompt = prompt['user'].format(
            chunk_text=chunk_text,
            student_questions=student_questions
        )
        return self._make_llm_call(prompt['system'], user_prompt)

    # Engage Module Methods
    def analyze_explanation(self, chunk_text: str, student_explanation: str) -> Optional[str]:
        """Analyze student's explanation of a section."""
        prompt = self._get_prompt('engage_module', 'explanation_analysis')
        if not prompt:
            return None
        
        user_prompt = prompt['user'].format(
            chunk_text=chunk_text,
            student_explanation=student_explanation
        )
        return self._make_llm_call(prompt['system'], user_prompt)

    def analyze_analogy(self, chunk_text: str, student_analogy: str) -> Optional[str]:
        """Analyze student's analogy for a concept."""
        prompt = self._get_prompt('engage_module', 'analogy_analysis')
        if not prompt:
            return None
        
        user_prompt = prompt['user'].format(
            chunk_text=chunk_text,
            student_analogy=student_analogy
        )
        return self._make_llm_call(prompt['system'], user_prompt)

    # Challenge Module Methods
    def analyze_critical_thinking(self, chunk_text: str, student_analysis: str) -> Optional[str]:
        """Analyze student's critical thinking about a section."""
        prompt = self._get_prompt('challenge_module', 'critical_analysis')
        if not prompt:
            return None
        
        user_prompt = prompt['user'].format(
            chunk_text=chunk_text,
            student_analysis=student_analysis
        )
        return self._make_llm_call(prompt['system'], user_prompt)

    def analyze_connections(self, chunk_text: str, student_connections: str) -> Optional[str]:
        """Analyze student's connections between concepts."""
        prompt = self._get_prompt('challenge_module', 'connection_analysis')
        if not prompt:
            return None
        
        user_prompt = prompt['user'].format(
            chunk_text=chunk_text,
            student_connections=student_connections
        )
        return self._make_llm_call(prompt['system'], user_prompt)

    # Solidify Module Methods
    def analyze_flashcards(self, chunk_text: str, student_flashcards: List[Dict[str, str]]) -> Optional[str]:
        """Analyze student's flashcards for a section."""
        prompt = self._get_prompt('solidify_module', 'flashcard_analysis')
        if not prompt:
            return None
        
        user_prompt = prompt['user'].format(
            chunk_text=chunk_text,
            student_flashcards=json.dumps(student_flashcards, indent=2)
        )
        return self._make_llm_call(prompt['system'], user_prompt)

    def analyze_application(self, chunk_text: str, student_application: str) -> Optional[str]:
        """Analyze student's application of concepts."""
        prompt = self._get_prompt('solidify_module', 'application_analysis')
        if not prompt:
            return None
        
        user_prompt = prompt['user'].format(
            chunk_text=chunk_text,
            student_application=student_application
        )
        return self._make_llm_call(prompt['system'], user_prompt)

    # Original methods (kept for backward compatibility)
    def get_simplicity_feedback(self, explanation: str) -> Optional[str]:
        """Get feedback on explanation simplicity and clarity."""
        return self.analyze_explanation("", explanation)  # Reuse explanation analysis

    def suggest_flashcards_with_context(self, formatted_context: str) -> Optional[List[Dict[str, str]]]:
        """
        Suggest flashcard Q/A pairs based on formatted learning context.

        This is the NEW preferred method that uses pre-formatted context from
        _build_learning_context() and _format_context_for_flashcards().

        Args:
            formatted_context: Pre-formatted string with all learning context

        Returns:
            List of flashcard dicts with 'question' and 'answer' keys
        """
        if not self.is_available():
            logger.warning("LLM service is not available. Please check your API key configuration.")
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
                    {"role": "system", "content": "You are a learning assistant creating effective flashcards. Always return valid JSON array."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
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
                else:
                    logger.error(f"Flashcard response is not a list: {type(qa_pairs)}")
                    return None
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse flashcard suggestions as JSON: {e}")
                logger.error(f"Attempted to parse: {json_str[:200]}")
                return None

        except Exception as e:
            logger.error(f"Error generating flashcard suggestions: {str(e)}", exc_info=True)
            return None

    def suggest_flashcards(self, chunk_text: str, user_explanation: str, user_challenges: str, existing_cards: List[Dict[str, str]] = None) -> Optional[List[Dict[str, str]]]:
        """Suggest flashcard Q/A pairs based on the material and user's understanding."""
        if not self.is_available():
            logger.warning("LLM service is not available. Please check your API key configuration.")
            return None

        try:
            # Build existing cards context if provided
            existing_context = ""
            if existing_cards and len(existing_cards) > 0:
                existing_context = "\n\nPreviously suggested flashcards (DO NOT duplicate these):\n"
                for i, card in enumerate(existing_cards, 1):
                    existing_context += f"{i}. Q: {card['question']}\n   A: {card['answer']}\n"
                existing_context += "\nGenerate NEW flashcards on different aspects of the material."

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
                    {"role": "system", "content": "You are a helpful learning assistant focused on creating effective flashcards. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
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
                else:
                    logger.error(f"Flashcard response is not a list: {type(qa_pairs)}")
                    return None
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse flashcard suggestions as JSON: {e}")
                logger.error(f"Attempted to parse: {json_str[:200]}")
                return None

        except Exception as e:
            logger.error(f"Error generating flashcard suggestions: {str(e)}")
            return None 