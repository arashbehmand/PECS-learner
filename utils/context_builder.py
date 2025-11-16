"""
Context Engineering Utilities for AI Features

This module provides DRY (Don't Repeat Yourself) utilities for building
comprehensive learning context from section state. Used across all AI features
to ensure consistent, high-quality context.

Includes support for rolling context - cumulative summaries of previous sections
based on material sequence (not user progress).
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def build_learning_context(
    section_content: str,
    pecs_data: Dict[str, Any],
    flashcards: List[Dict[str, str]] = None,
    include_conversations: bool = False,
    rolling_summary: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build comprehensive learning context from section state.

    This is the SINGLE SOURCE OF TRUTH for what AI knows about student's journey.
    Used by all AI features: flashcard generation, completion reports, feedback, etc.

    Args:
        section_content: The original learning material
        pecs_data: Section's PECS data (phases, conversations, completion)
        flashcards: List of committed DB flashcards (NOT ephemeral suggestions)
        include_conversations: Whether to include conversation history
        rolling_summary: Optional summary of previous sections (rolling context)

    Returns:
        Dictionary with comprehensive learning context
    """
    context = {
        "content": section_content,
        "understanding": None,  # Prime phase
        "explanation": None,  # Engage phase
        "critical_thinking": None,  # Challenge phase
        "conversations": {},
        "flashcards": flashcards or [],
        "rolling_summary": rolling_summary,  # Context from previous sections
    }

    # Extract Prime phase data
    prime_data = pecs_data.get("prime_preview", {})
    context["understanding"] = prime_data.get("understanding")

    # Extract Engage phase data
    engage_data = pecs_data.get("engage_explain", {})
    context["explanation"] = engage_data.get("explanation")

    # Extract Challenge phase data
    challenge_data = pecs_data.get("challenge_connect", {})
    context["critical_thinking"] = challenge_data.get(
        "critical_questions"
    ) or challenge_data.get("critical_thinking")

    # Include conversations if requested (expensive, only for specific features)
    if include_conversations:
        for phase_key in ["prime_preview", "engage_explain", "challenge_connect"]:
            phase_data = pecs_data.get(phase_key, {})
            conversation = phase_data.get("ai_conversation", [])
            if conversation:
                context["conversations"][phase_key] = conversation

    logger.debug(
        f"Built context: {len(context['flashcards'])} flashcards, "
        f"{len(context['conversations'])} conversations, "
        f"understanding={'present' if context['understanding'] else 'missing'}"
    )

    return context


def format_context_for_flashcards(context: Dict[str, Any]) -> str:
    """
    Format learning context specifically for flashcard generation.

    Creates a clear, well-structured prompt with visual separators to help
    the AI understand what content is available and what to avoid duplicating.

    Args:
        context: Dictionary from build_learning_context()

    Returns:
        Formatted string ready for LLM prompt
    """
    parts = []

    # Section content (truncated to avoid token limits)
    parts.append("=" * 60)
    parts.append("LEARNING MATERIAL")
    parts.append("=" * 60)
    parts.append(
        context["content"][:1500] + ("..." if len(context["content"]) > 1500 else "")
    )
    parts.append("")

    # Student's learning journey
    if context.get("understanding"):
        parts.append("=" * 60)
        parts.append("STUDENT'S INITIAL UNDERSTANDING (Prime Phase)")
        parts.append("=" * 60)
        parts.append(context["understanding"])
        parts.append("")

    if context.get("explanation"):
        parts.append("=" * 60)
        parts.append("STUDENT'S EXPLANATION (Engage Phase)")
        parts.append("=" * 60)
        parts.append(context["explanation"])
        parts.append("")

    if context.get("critical_thinking"):
        parts.append("=" * 60)
        parts.append("STUDENT'S CRITICAL ANALYSIS (Challenge Phase)")
        parts.append("=" * 60)
        parts.append(context["critical_thinking"])
        parts.append("")

    # Existing flashcards (CRITICAL: prevents duplicates)
    if context.get("flashcards"):
        parts.append("=" * 60)
        parts.append(
            f"EXISTING FLASHCARDS ({len(context['flashcards'])} cards - DO NOT DUPLICATE)"
        )
        parts.append("=" * 60)
        for i, card in enumerate(context["flashcards"], 1):
            parts.append(f"\n{i}. Q: {card['question']}")
            parts.append(f"   A: {card['answer']}")
        parts.append("")
        parts.append(
            "⚠️  Generate DIFFERENT flashcards covering new aspects not in the list above."
        )
        parts.append("")

    return "\n".join(parts)


def format_context_for_completion(context: Dict[str, Any]) -> str:
    """
    Format learning context for completion report generation.

    Includes conversations to give AI full picture of learning journey.

    Args:
        context: Dictionary from build_learning_context(include_conversations=True)

    Returns:
        Formatted string ready for LLM prompt
    """
    parts = []

    # Section content
    parts.append("=" * 60)
    parts.append("LEARNING MATERIAL")
    parts.append("=" * 60)
    parts.append(
        context["content"][:2000] + ("..." if len(context["content"]) > 2000 else "")
    )
    parts.append("")

    # Learning journey with conversations
    phase_names = {
        "prime_preview": "PRIME & PREVIEW",
        "engage_explain": "ENGAGE & EXPLAIN",
        "challenge_connect": "CHALLENGE & CONNECT",
    }

    for phase_key, phase_name in phase_names.items():
        conversation = context.get("conversations", {}).get(phase_key, [])
        if conversation:
            parts.append("=" * 60)
            parts.append(f"{phase_name} - Learning Conversation")
            parts.append("=" * 60)
            for msg in conversation:
                role = msg.get("role", "unknown").upper()
                content = msg.get("content", "")
                parts.append(f"[{role}]: {content}")
            parts.append("")

    # Direct responses (if no conversations)
    if context.get("understanding"):
        parts.append("=" * 60)
        parts.append("INITIAL UNDERSTANDING")
        parts.append("=" * 60)
        parts.append(context["understanding"])
        parts.append("")

    if context.get("explanation"):
        parts.append("=" * 60)
        parts.append("STUDENT'S EXPLANATION")
        parts.append("=" * 60)
        parts.append(context["explanation"])
        parts.append("")

    if context.get("critical_thinking"):
        parts.append("=" * 60)
        parts.append("CRITICAL ANALYSIS")
        parts.append("=" * 60)
        parts.append(context["critical_thinking"])
        parts.append("")

    # Flashcards created
    if context.get("flashcards"):
        parts.append("=" * 60)
        parts.append(f"FLASHCARDS CREATED ({len(context['flashcards'])} cards)")
        parts.append("=" * 60)
        for i, card in enumerate(context["flashcards"], 1):
            parts.append(f"{i}. Q: {card['question']}")
            parts.append(f"   A: {card['answer']}")
        parts.append("")

    return "\n".join(parts)


def format_context_with_rolling_summary(context: Dict[str, Any]) -> str:
    """
    Format learning context for PECS AI feedback, including rolling summary.

    This version includes the rolling context from previous sections to give AI
    better understanding of the material's narrative flow.

    Args:
        context: Dictionary from build_learning_context(rolling_summary=...)

    Returns:
        Formatted string ready for LLM prompt
    """
    parts = []

    # Rolling summary from previous sections (if available)
    if context.get("rolling_summary"):
        parts.append("=" * 60)
        parts.append("PREVIOUS SECTIONS SUMMARY (Rolling Context)")
        parts.append("=" * 60)
        parts.append(context["rolling_summary"])
        parts.append("")
        parts.append("⬇️  The current section builds upon this foundation")
        parts.append("")

    # Current section content
    parts.append("=" * 60)
    parts.append("CURRENT SECTION")
    parts.append("=" * 60)
    parts.append(
        context["content"][:2000] + ("..." if len(context["content"]) > 2000 else "")
    )
    parts.append("")

    return "\n".join(parts)
