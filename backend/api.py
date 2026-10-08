import os
import uuid
from typing import Optional

def ingest_file(path: str) -> dict:
    """Stub for ingesting a study document."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    # Simulate basic ingestion
    return {
        "doc_id": str(uuid.uuid4()),
        "name": os.path.basename(path),
        "chunks": 42
    }

def list_documents() -> list[dict]:
    """Stub for listing ingested documents."""
    return [
        {
            "doc_id": "dummy-doc-1234",
            "name": "sample_notes.txt"
        }
    ]

def ask(question: str, doc_id: Optional[str] = None, top_k: int = 4, history: Optional[list[dict]] = None) -> dict:
    """Stub for RAG QA."""
    return {
        "answer": f"This is a simulated answer to your question: '{question}'",
        "sources": [
            {
                "file": "sample_notes.txt",
                "page": 1,
                "snippet": "Simulated source text relevant to the query."
            }
        ]
    }

def summarize(doc_id: str) -> str:
    """Stub for summarization."""
    return "This is a simulated summary of the requested document. It outlines the main concepts covered in the text."

def generate_quiz(doc_id: str, n: int = 5) -> list[dict]:
    """Stub for generating a multiple-choice quiz."""
    quiz = []
    for i in range(n):
        quiz.append({
            "question": f"Sample Question {i+1}?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer_index": 0,
            "explanation": "Option A is correct because of simulated reasons."
        })
    return quiz

def generate_flashcards(doc_id: str, n: int = 10) -> list[dict]:
    """Stub for generating flashcards."""
    flashcards = []
    for i in range(n):
        flashcards.append({
            "front": f"Sample Concept {i+1}",
            "back": f"Explanation for Sample Concept {i+1}"
        })
    return flashcards

def delete_document(doc_id: str) -> bool:
    """Stub for deleting a document."""
    return True
