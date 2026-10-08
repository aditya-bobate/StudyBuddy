"""Stable public API used by the StudyBuddy Streamlit application."""

from __future__ import annotations

import logging

from .ingest import delete_document as _delete_document
from .ingest import ingest_file as _ingest_file
from .ingest import list_documents as _list_documents
from .quiz import generate_flashcards as _generate_flashcards
from .quiz import generate_quiz as _generate_quiz
from .quiz import summarize as _summarize
from .rag import answer_question

logger = logging.getLogger(__name__)


def ingest_file(path: str) -> dict:
    """Ingest a PDF/TXT file and return its document metadata."""
    return _ingest_file(path)


def list_documents() -> list[dict]:
    """List all documents currently stored by StudyBuddy."""
    return _list_documents()


def ask(
    question: str,
    doc_id: str | None = None,
    top_k: int = 4,
    history: list[dict] | None = None,
) -> dict:
    """Answer a question using retrieval-augmented generation."""
    return answer_question(question, doc_id=doc_id, top_k=top_k, history=history)


def summarize(doc_id: str) -> str:
    """Summarize one stored document."""
    return _summarize(doc_id)


def generate_quiz(doc_id: str, n: int = 5) -> list[dict]:
    """Generate validated multiple-choice questions from a document."""
    return _generate_quiz(doc_id, n=n)


def generate_flashcards(doc_id: str, n: int = 10) -> list[dict]:
    """Generate validated flashcards from a document."""
    return _generate_flashcards(doc_id, n=n)


def delete_document(doc_id: str) -> bool:
    """Delete all stored data belonging to a document."""
    return _delete_document(doc_id)
