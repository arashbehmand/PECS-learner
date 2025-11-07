import os
import json
import yaml
from typing import Optional, Dict, Any, List
import streamlit as st
from openai import OpenAI
from openai.types.chat import ChatCompletion

class LLMService:
    def __init__(self):
        """Initialize the LLM service with API key from Streamlit secrets."""
        try:
            # Load prompts from YAML
            with open('utils/prompts.yaml', 'r') as f:
                self.prompts = yaml.safe_load(f)
            
            # Try to get the API key
            if "llm" in st.secrets:
                self.api_key = st.secrets["llm"]["openai_api_key"]
            else:
                self.api_key = None
            
            # Initialize client if we have an API key
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
            else:
                self.client = None
                
            self.model = "gpt-3.5-turbo"  # Default to a cost-effective model
            
        except Exception as e:
            st.error(f"Error initializing LLM service: {str(e)}")
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
            st.error(f"Prompt template not found: {module}.{prompt_type}")
            return None

    def _make_llm_call(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Make a call to the LLM API."""
        if not self.is_available():
            st.warning("LLM service is not available. Please check your API key configuration.")
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
            st.error(f"Error making LLM call: {str(e)}")
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

    def suggest_flashcards(self, chunk_text: str, user_explanation: str, user_challenges: str) -> Optional[List[Dict[str, str]]]:
        """Suggest flashcard Q/A pairs based on the material and user's understanding."""
        if not self.is_available():
            st.warning("LLM service is not available. Please check your API key configuration.")
            return None

        try:
            prompt = f"""Based on the following learning material and the user's understanding, 
            suggest 2-3 high-quality flashcard Q/A pairs that would help reinforce key concepts.
            
            Original Material:
            {chunk_text}
            
            User's Explanation:
            {user_explanation}
            
            User's Challenges/Questions:
            {user_challenges}
            
            For each flashcard:
            1. Question should be clear and test understanding
            2. Answer should be concise but complete
            3. Focus on key concepts and relationships
            4. Avoid trivial or obvious questions
            
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
            try:
                qa_pairs = json.loads(content)
                if isinstance(qa_pairs, list):
                    return qa_pairs[:3]  # Return at most 3 pairs
            except json.JSONDecodeError:
                st.error("Failed to parse flashcard suggestions as JSON")
                return None

        except Exception as e:
            st.error(f"Error generating flashcard suggestions: {str(e)}")
            return None 