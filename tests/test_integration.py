import os

import pytest
import requests

from backend.api import (
    ask,
    delete_document,
    generate_flashcards,
    generate_quiz,
    ingest_file,
    list_documents,
    summarize,
)
from backend.errors import EmptyDocument


def is_ollama_running():
    try:
        response = requests.get(os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        return response.status_code == 200
    except requests.ConnectionError:
        return False

@pytest.mark.skipif(not is_ollama_running(), reason="Ollama is not available.")
def test_full_integration_flow():
    """Test the end-to-end integration flow."""
    sample_txt = "sample_data/biology_notes.txt"
    if not os.path.exists(sample_txt):
        pytest.skip("Sample data missing.")

    # Create a dummy PDF file for testing PDF ingestion
    from pypdf import PdfWriter
    dummy_pdf_path = "sample_data/dummy.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with open(dummy_pdf_path, "wb") as f:
        writer.write(f)

    try:
        # 1. Ingest TXT
        ingest_txt_res = ingest_file(sample_txt)
        txt_doc_id = ingest_txt_res["doc_id"]
        assert ingest_txt_res["chunks"] > 0

        # 1. Ingest PDF (empty)
        try:
            ingest_file(dummy_pdf_path)
            pdf_doc_id = None
        except EmptyDocument as e:
            assert "empty" in str(e).lower()
            pdf_doc_id = None

        # 2. List
        docs = list_documents()
        doc_ids = [d["doc_id"] for d in docs]
        assert txt_doc_id in doc_ids
        if pdf_doc_id:
            assert pdf_doc_id in doc_ids

        # 3. Ask with document filter
        ask_res_filtered = ask("Explain mitochondria", doc_id=txt_doc_id)
        assert "answer" in ask_res_filtered
        assert len(ask_res_filtered["answer"]) > 0
        assert "sources" in ask_res_filtered

        # 3. Ask without document filter
        ask_res_unfiltered = ask("Explain biology")
        assert "answer" in ask_res_unfiltered
        assert len(ask_res_unfiltered["answer"]) > 0
        assert "sources" in ask_res_unfiltered

        # 4. Summarize
        summary = summarize(txt_doc_id)
        assert len(summary) > 0

        # 5. Quiz JSON validation
        quiz = generate_quiz(txt_doc_id, n=2)
        assert isinstance(quiz, list)
        assert len(quiz) == 2
        for q in quiz:
            assert "question" in q
            assert "options" in q
            assert isinstance(q["options"], list)
            assert len(q["options"]) == 4
            assert "answer_index" in q
            assert isinstance(q["answer_index"], int)
            assert 0 <= q["answer_index"] <= 3
            assert "explanation" in q

        # 6. Flashcard validation
        flashcards = generate_flashcards(txt_doc_id, n=2)
        assert isinstance(flashcards, list)
        assert len(flashcards) == 2
        for f in flashcards:
            assert "front" in f
            assert "back" in f

        # 7. Deletion
        del_res = delete_document(txt_doc_id)
        assert del_res is True
        if pdf_doc_id:
            del_pdf_res = delete_document(pdf_doc_id)
            assert del_pdf_res is True

        # Ensure it's deleted
        docs_after = list_documents()
        doc_ids_after = [d["doc_id"] for d in docs_after]
        assert txt_doc_id not in doc_ids_after
        if pdf_doc_id:
            assert pdf_doc_id not in doc_ids_after

    finally:
        if os.path.exists(dummy_pdf_path):
            os.remove(dummy_pdf_path)
