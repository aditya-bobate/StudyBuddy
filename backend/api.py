"""Stable public API used by the StudyBuddy Streamlit application."""

from __future__ import annotations

from .ingest import delete_document as _delete_document
from .ingest import ingest_file as _ingest_file
from .ingest import list_documents as _list_documents
from .quiz import generate_flashcards as _generate_flashcards
from .quiz import generate_quiz as _generate_quiz
from .quiz import summarize as _summarize
from .rag import answer_question


def ask(question: str, doc_id: str | None = None, top_k: int = 4, history=None) -> dict:
    """Answer a question using retrieved document context."""
    return answer_question(
        question,
        doc_id=doc_id,
        top_k=top_k,
        history=history,
    )


def delete_document(doc_id: str) -> bool:
    """Delete a stored study document."""
    return _delete_document(doc_id)


def ingest_file(path: str) -> dict:
    return _ingest_file(path)


def list_documents() -> list[dict]:
    return _list_documents()


def summarize(doc_id: str) -> str:
    return _summarize(doc_id)


def generate_quiz(doc_id: str, n: int = 5) -> list[dict]:
    return _generate_quiz(doc_id, n)


def generate_flashcards(doc_id: str, n: int = 10) -> list[dict]:
    return _generate_flashcards(doc_id, n)
