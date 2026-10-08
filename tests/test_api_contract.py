import os

import pytest

from backend.api import (
    ask,
    delete_document,
    generate_flashcards,
    generate_quiz,
    ingest_file,
    list_documents,
    summarize,
)
from backend.errors import OllamaNotRunning


def test_ingest_file():
    """Test the structure of the ingest_file return dictionary."""
    sample_path = "sample_data/biology_notes.txt"
    if not os.path.exists(sample_path):
        pytest.skip("Sample data missing.")

    try:
        result = ingest_file(sample_path)
    except OllamaNotRunning:
        pytest.skip("Ollama is not running")

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
    try:
        result = ask("What is the cell theory?")
    except OllamaNotRunning:
        pytest.skip("Ollama is not running")

    assert isinstance(result, dict)
    assert "answer" in result
    assert "sources" in result
    assert isinstance(result["answer"], str)
    assert isinstance(result["sources"], list)
    for source in result["sources"]:
        assert "file" in source
        assert "page" in source
        assert "snippet" in source


@pytest.fixture(scope="module")
def sample_doc_id():
    sample_path = "sample_data/biology_notes.txt"
    if not os.path.exists(sample_path):
        pytest.skip("Sample data missing.")
    try:
        res = ingest_file(sample_path)
    except OllamaNotRunning:
        pytest.skip("Ollama is not available in this environment.")
    return res["doc_id"]


def test_summarize(sample_doc_id):
    """Test the summarize return type."""
    result = summarize(sample_doc_id)
    assert isinstance(result, str)
    with pytest.raises(ValueError, match="Document 'dummy-id' was not found."):
        summarize("dummy-id")


def test_generate_quiz(sample_doc_id):
    """Test the structure of the generate_quiz return list."""
    result = generate_quiz(sample_doc_id, n=3)
    assert isinstance(result, list)
    assert len(result) == 3
    for q in result:
        assert "question" in q
        assert "options" in q
        assert "answer_index" in q
        assert "explanation" in q
        assert isinstance(q["options"], list)
        assert len(q["options"]) == 4
    with pytest.raises(ValueError, match="Document 'dummy-id' was not found."):
        generate_quiz("dummy-id", n=3)


def test_generate_flashcards(sample_doc_id):
    """Test the structure of the generate_flashcards return list."""
    result = generate_flashcards(sample_doc_id, n=2)
    assert isinstance(result, list)
    assert len(result) == 2
    for card in result:
        assert "front" in card
        assert "back" in card
    with pytest.raises(ValueError, match="Document 'dummy-id' was not found."):
        generate_flashcards("dummy-id", n=2)


def test_delete_document(sample_doc_id):
    """Test the delete_document return type."""
    result = delete_document(sample_doc_id)
    assert isinstance(result, bool)


def test_ingest_file_missing_path():
    """Test that ingest_file raises FileNotFoundError for a missing path."""
    with pytest.raises(FileNotFoundError):
        ingest_file("sample_data/does_not_exist.txt")


def test_generate_quiz_zero_items():
    """Test that requesting zero quiz questions returns an empty list."""
    result = generate_quiz("dummy-id", n=0)
    assert isinstance(result, list)
    assert result == []


def test_generate_flashcards_zero_items():
    """Test that requesting zero flashcards returns an empty list."""
    result = generate_flashcards("dummy-id", n=0)
    assert isinstance(result, list)
    assert result == []
