import os
import sys

import streamlit as st

# Add the project root to the Python path so the frontend can find the backend module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import backend API functions (currently stubs)
from backend.api import (  # noqa: F401
    ask,
    delete_document,
    generate_flashcards,
    generate_quiz,
    ingest_file,
    list_documents,
    summarize,
)

def main() -> None:
    """Main Streamlit application entry point."""

    st.set_page_config(
        page_title="StudyBuddy",
        page_icon="📚",
        layout="centered"
    )

    with st.sidebar:
        st.title("📚 StudyBuddy")
        st.caption("Settings and navigation")
        st.divider()

    st.title("StudyBuddy")
    st.write(
        "Your offline AI study assistant. Chat with your notes, "
        "generate quizzes, and review flashcards."
    )
    st.divider()

    st.info("Upload a file to start.")


if __name__ == "__main__":
    main()