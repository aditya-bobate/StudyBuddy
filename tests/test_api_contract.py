import os
import pytest
from backend.api import (
    ingest_file,
    list_documents,
    ask,
    summarize,
    generate_quiz,
    generate_flashcards,
    delete_document,
)

def test_ingest_file():
    """Test the structure of the ingest_file return dictionary."""
    sample_path = "sample_data/biology_notes.txt"
    if not os.path.exists(sample_path):
        pytest.skip("Sample data missing.")
        
    result = ingest_file(sample_path)
    assert isinstance(result, dict)
    assert "doc_id" in result
    assert "name" in result
    assert "chunks" in result
    assert isinstance(result["doc_id"], str)
    assert isinstance(result["name"], str)
    assert isinstance(result["chunks"], int)

def test_list_documents():
    """Test the structure of the list_documents return list."""
    result = list_documents()
    assert isinstance(result, list)
    for doc in result:
        assert "doc_id" in doc
        assert "name" in doc
        assert isinstance(doc["doc_id"], str)
        assert isinstance(doc["name"], str)

def test_ask():
    """Test the structure of the ask return dictionary."""
    result = ask("What is the cell theory?")
    assert isinstance(result, dict)
    assert "answer" in result
    assert "sources" in result
    assert isinstance(result["answer"], str)
    assert isinstance(result["sources"], list)
    for source in result["sources"]:
        assert "file" in source
        assert "page" in source
        assert "snippet" in source

def test_summarize():
    """Test the summarize return type."""
    result = summarize("dummy-id")
    assert isinstance(result, str)

def test_generate_quiz():
    """Test the structure of the generate_quiz return list."""
    result = generate_quiz("dummy-id", n=3)
    assert isinstance(result, list)
    assert len(result) == 3
    for q in result:
        assert "question" in q
        assert "options" in q
        assert "answer_index" in q
        assert "explanation" in q
        assert isinstance(q["options"], list)
        assert len(q["options"]) == 4

def test_generate_flashcards():
    """Test the structure of the generate_flashcards return list."""
    result = generate_flashcards("dummy-id", n=2)
    assert isinstance(result, list)
    assert len(result) == 2
    for card in result:
        assert "front" in card
        assert "back" in card

def test_delete_document():
    """Test the delete_document return type."""
    result = delete_document("dummy-id")
    assert isinstance(result, bool)
