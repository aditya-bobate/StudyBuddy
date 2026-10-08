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

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.title("📚 StudyBuddy")
        st.caption("Settings and navigation")
        st.divider()

        # Upload notes
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
            st.session_state["selected_doc_id"] = None

    # Main page
    st.title("StudyBuddy")
    st.caption("Chat with your study notes using offline AI.")

    selected_doc_id = st.session_state.get("selected_doc_id")

    if not selected_doc_id:
        st.info("Upload and select a document to start chatting.")
        return

    st.success("Document selected. Ask anything about your notes! 📖")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                with st.expander("📚 Sources"):
                    for source in message["sources"]:
                        st.markdown(
                            f"**{source['file']}** — "
                            f"Page {source['page']}"
                        )
                        st.caption(source["snippet"])

    # Chat input
    question = st.chat_input("Ask a question about your notes...")

    if question:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        history = [
            {
                "role": message["role"],
                "content": message["content"],
            }
            for message in st.session_state.messages[:-1]
        ]

        with st.chat_message("assistant"), st.spinner("Thinking..."):
            try:
                response = ask(
                    question,
                    doc_id=selected_doc_id,
                    top_k=4,
                    history=history,
                )

                answer = response["answer"]
                sources = response.get("sources", [])

                st.markdown(answer)

                if sources:
                    with st.expander("📚 Sources"):
                        for source in sources:
                            st.markdown(
                                f"**{source['file']}** — "
                                f"Page {source['page']}"
                            )
                            st.caption(source["snippet"])

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

            except Exception as exc:  # noqa: BLE001
                error_message = f"Unable to answer: {exc}"
                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )


if __name__ == "__main__":
    main()