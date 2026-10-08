import os
import pytest
import requests
from backend.api import (
    ingest_file,
    list_documents,
    ask,
    summarize,
    generate_quiz,
    generate_flashcards,
)

def is_ollama_running():
    try:
        response = requests.get(os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        return response.status_code == 200
    except requests.ConnectionError:
        return False

@pytest.mark.skipif(not is_ollama_running(), reason="Ollama is not available.")
def test_full_integration_flow():
    """Test the end-to-end integration flow."""
    sample_path = "sample_data/biology_notes.txt"
    if not os.path.exists(sample_path):
        pytest.skip("Sample data missing.")
        
    # 1. Ingest
    ingest_res = ingest_file(sample_path)
    doc_id = ingest_res["doc_id"]
    
    # 2. List
    docs = list_documents()
    assert len(docs) > 0
    
    # 3. Ask
    ask_res = ask("Explain mitochondria", doc_id=doc_id)
    assert "answer" in ask_res
    
    # 4. Summarize
    summary = summarize(doc_id)
    assert len(summary) > 0
    
    # 5. Quiz
    quiz = generate_quiz(doc_id, n=2)
    assert len(quiz) == 2
    
    # 6. Flashcards
    flashcards = generate_flashcards(doc_id, n=2)
    assert len(flashcards) == 2
