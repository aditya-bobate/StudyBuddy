"""Stable public API used by the StudyBuddy Streamlit application."""

from __future__ import annotations

from .ingest import (
    delete_document,
    ingest_file,
    list_documents,
)
from .quiz import (
    generate_flashcards,
    generate_quiz,
    summarize,
)
from .rag import answer_question


def ask(question: str, doc_id: str | None = None, top_k: int = 4, history=None) -> dict:
    """Answer a question using retrieved document context."""
    return answer_question(
        question,
        doc_id=doc_id,
        top_k=top_k,
        history=history,
    )
