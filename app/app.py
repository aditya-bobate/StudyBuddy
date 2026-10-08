import os
import sys
import tempfile

import streamlit as st

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import backend API functions
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
        layout="centered",
    )

    with st.sidebar:
        st.title("📚 StudyBuddy")
        st.caption("Settings and navigation")
        st.divider()

        # File upload
        st.subheader("Upload notes")

        uploaded_file = st.file_uploader(
            "Choose a PDF or TXT file",
            type=["pdf", "txt"],
        )

        if uploaded_file is not None and st.button(
            "Upload & Index",
            use_container_width=True,
        ):
            suffix = os.path.splitext(uploaded_file.name)[1]

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
            ) as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                temp_path = temp_file.name

            try:
                result = ingest_file(temp_path)

                st.success(
                    f"Uploaded {result['name']} "
                    f"({result['chunks']} chunks)"
                )
                st.rerun()
            except Exception as exc:  # noqa: BLE001
                st.error(f"Upload failed: {exc}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        st.divider()

        # Document selector
        st.subheader("Your documents")

        try:
            documents = list_documents()
        except Exception as exc:  # noqa: BLE001
            documents = []
            st.error(f"Could not load documents: {exc}")

        if documents:
            document_options = {
                document["name"]: document["doc_id"]
                for document in documents
            }

            selected_name = st.selectbox(
                "Select a document",
                options=list(document_options.keys()),
            )

            st.session_state["selected_doc_id"] = document_options[
                selected_name
            ]
        else:
            st.info("No documents uploaded yet.")

    st.title("StudyBuddy")
    st.write(
        "Your offline AI study assistant. Chat with your notes, "
        "generate quizzes, and review flashcards."
    )
    st.divider()

    selected_doc_id = st.session_state.get("selected_doc_id")

    if selected_doc_id:
        st.success("Document selected. Ready to study! 📖")
    else:
        st.info("Upload a file from the sidebar to start.")


if __name__ == "__main__":
    main()