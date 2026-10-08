"""LLM-powered summaries, quizzes, and flashcards with defensive JSON parsing."""

from __future__ import annotations

import json
import re

from .ingest import get_document_chunks
from .llm import chat


def _document_context(doc_id: str) -> str:
    """Build a bounded text context from all chunks of one document."""
    chunks = get_document_chunks(doc_id)
    if not chunks:
        raise ValueError(f"Document '{doc_id}' was not found.")
    # Keep prompts bounded for local models while preserving the document order.
    parts: list[str] = []
    total_chars = 0
    max_chars = 30000
    for item in chunks:
        part = f"[Page {item['page']}] {item['text']}"
        if parts and total_chars + len(part) > max_chars:
            break
        parts.append(part)
        total_chars += len(part)
    return "\n\n".join(parts)


def _extract_json(text: str):
    """Parse JSON even when a model wraps it in Markdown code fences."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", cleaned)
        if not match:
            raise
        return json.loads(match.group(1))


def _ask_json(prompt: str):
    """Request JSON from the model and retry once when parsing fails."""
    response = chat(prompt)
    try:
        return _extract_json(response)
    except (json.JSONDecodeError, TypeError):
        retry_prompt = (
            prompt
            + "\n\nYour previous response was invalid JSON. Return ONLY valid JSON, with no Markdown, commentary, or code fences."
        )
        return _extract_json(chat(retry_prompt))


def summarize(doc_id: str) -> str:
    """Generate a concise study summary grounded in the document."""
    context = _document_context(doc_id)
    return chat(
        f"Summarize the following study material. Cover the main concepts, definitions, "
        f"and important relationships. Do not add information not present in the material.\n\n{context}",
        system="You are a study-note summarizer. Be accurate and concise.",
    )


def generate_quiz(doc_id: str, n: int = 5) -> list[dict]:
    """Generate n validated multiple-choice questions from a document."""
    if n < 0:
        raise ValueError("n must be non-negative.")
    if n == 0:
        return []
    context = _document_context(doc_id)
    data = _ask_json(
        f"""Create exactly {n} multiple-choice questions from this study material.
Return ONLY a JSON array. Each item must have exactly these keys:
question (string), options (array of exactly 4 strings), answer_index (integer 0-3), explanation (string).
Questions and answers must be supported by the material.

Study material:
{context}"""
    )
    if not isinstance(data, list) or len(data) != n:
        raise ValueError("The model returned an invalid quiz structure.")
    validated = []
    for item in data:
        if not isinstance(item, dict):
            raise TypeError("The model returned an invalid quiz item.")
        options = item.get("options")
        answer_index = item.get("answer_index")
        if (
            not isinstance(item.get("question"), str)
            or not isinstance(options, list)
            or len(options) != 4
        ):
            raise ValueError("The model returned an invalid quiz item.")
        if not isinstance(answer_index, int) or not 0 <= answer_index <= 3:
            raise ValueError("The model returned an invalid answer index.")
        validated.append(
            {
                "question": item["question"],
                "options": [str(option) for option in options],
                "answer_index": answer_index,
                "explanation": str(item.get("explanation", "")),
            }
        )
    return validated


def generate_flashcards(doc_id: str, n: int = 10) -> list[dict]:
    """Generate n concise front/back flashcards from a document."""
    if n < 0:
        raise ValueError("n must be non-negative.")
    if n == 0:
        return []
    context = _document_context(doc_id)
    data = _ask_json(
        f"""Create exactly {n} useful study flashcards from this material.
Return ONLY a JSON array. Each item must contain exactly: front (string), back (string).
Keep answers concise and use only information present in the material.

Study material:
{context}"""
    )
    if not isinstance(data, list) or len(data) != n:
        raise ValueError("The model returned an invalid flashcard structure.")
    validated = []
    for item in data:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("front"), str)
            or not isinstance(item.get("back"), str)
        ):
            raise TypeError("The model returned an invalid flashcard item.")
        validated.append({"front": item["front"], "back": item["back"]})
    return validated
