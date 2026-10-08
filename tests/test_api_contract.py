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


def test_ingest_file():
    """Validate the ingest_file response contract."""
    sample_path = "sample_data/biology_notes.txt"
    if not os.path.exists(sample_path):
        pytest.skip("Sample data missing.")

    result = ingest_file(sample_path)

    assert isinstance(result, dict)
    assert set(result) >= {"doc_id", "name", "chunks"}
    assert isinstance(result["doc_id"], str)
    assert result["doc_id"]
    assert isinstance(result["name"], str)
    assert result["name"]
    assert isinstance(result["chunks"], int)
    assert result["chunks"] >= 0


def test_list_documents():
    """Validate the list_documents response contract."""
    result = list_documents()

    assert isinstance(result, list)

    for doc in result:
        assert set(doc) >= {"doc_id", "name"}
        assert isinstance(doc["doc_id"], str)
        assert doc["doc_id"]
        assert isinstance(doc["name"], str)
        assert doc["name"]


def test_ask():
    """Validate the ask response and source contracts."""
    result = ask("What is the cell theory?")

    assert isinstance(result, dict)
    assert set(result) >= {"answer", "sources"}
    assert isinstance(result["answer"], str)
    assert isinstance(result["sources"], list)

    for source in result["sources"]:
        assert set(source) >= {"file", "page", "snippet"}
        assert isinstance(source["file"], str)
        assert source["file"]
        assert source["page"] is None or isinstance(source["page"], int)
        assert isinstance(source["snippet"], str)
        assert source["snippet"]


def test_summarize():
    """Validate the summarize return type."""
    result = summarize("dummy-id")

    assert isinstance(result, str)


def test_generate_quiz():
    """Validate the quiz item contract."""
    result = generate_quiz("dummy-id", n=3)

    assert isinstance(result, list)
    assert len(result) == 3

    for question in result:
        assert set(question) >= {
            "question",
            "options",
            "answer_index",
            "explanation",
        }
        assert isinstance(question["question"], str)
        assert question["question"]
        assert isinstance(question["options"], list)
        assert len(question["options"]) == 4
        assert all(isinstance(option, str) for option in question["options"])
        assert isinstance(question["answer_index"], int)
        assert 0 <= question["answer_index"] < 4
        assert isinstance(question["explanation"], str)


def test_generate_flashcards():
    """Validate the flashcard item contract."""
    result = generate_flashcards("dummy-id", n=2)

    assert isinstance(result, list)
    assert len(result) == 2

    for card in result:
        assert set(card) >= {"front", "back"}
        assert isinstance(card["front"], str)
        assert card["front"]
        assert isinstance(card["back"], str)
        assert card["back"]


def test_delete_document():
    """Validate the delete_document return type."""
    result = delete_document("dummy-id")

    assert isinstance(result, bool)