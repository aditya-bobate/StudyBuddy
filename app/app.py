import csv
import io
import os
import sys
import tempfile

import streamlit as st

# Add project root so the app can import backend.api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.api import (
    ask,
    delete_document,
    generate_flashcards,
    generate_quiz,
    ingest_file,
    list_documents,
    summarize,
)

# -------------------------------------------------------------------
# Page configuration and styling
# -------------------------------------------------------------------

st.set_page_config(
    page_title="StudyBuddy",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css() -> None:
    """Apply simple custom styling to the application."""
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }

        .studybuddy-title {
            font-size: 2.7rem;
            font-weight: 750;
            margin-bottom: 0.2rem;
        }

        .studybuddy-subtitle {
            color: #9ca3af;
            font-size: 1.05rem;
            margin-bottom: 1.5rem;
        }

        .feature-card {
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid rgba(128, 128, 128, 0.25);
            margin-bottom: 0.8rem;
        }

        .score-card {
            padding: 1.2rem;
            border-radius: 14px;
            border: 1px solid rgba(128, 128, 128, 0.25);
            text-align: center;
            margin: 1rem 0;
        }

        .about-text {
            color: #9ca3af;
            font-size: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------
# Session state
# -------------------------------------------------------------------


def initialize_state() -> None:
    """Initialize all Streamlit session state values."""
    defaults = {
        "messages": [],
        "selected_doc_id": None,
        "quiz_data": [],
        "quiz_answers": {},
        "quiz_submitted": False,
        "flashcards": [],
        "flashcard_index": 0,
        "flashcard_flipped": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# -------------------------------------------------------------------
# Friendly backend errors
# -------------------------------------------------------------------


def show_backend_error(error: Exception, action: str) -> None:
    """Show a useful message for common backend failures."""
    error_name = type(error).__name__
    error_text = str(error)

    if error_name == "OllamaNotRunning":
        st.error("Ollama is not running.")
        st.info("How to fix: start Ollama and try again.")

    elif error_name == "ModelMissing":
        st.error("The required AI model is missing.")
        st.info(
            "How to fix: pull the configured Ollama model and try again."
        )

    elif error_name == "EmptyDocument":
        st.error("This document does not contain readable text.")
        st.info(
            "How to fix: use a text-based PDF/TXT file. "
            "Scanned image-only PDFs may not work."
        )

    elif error_name == "UnsupportedFile":
        st.error("This file type is not supported.")
        st.info("How to fix: upload a PDF or TXT file.")

    else:
        st.error(f"{action} failed: {error_text}")


# -------------------------------------------------------------------
# Document loading
# -------------------------------------------------------------------


def get_documents() -> list[dict]:
    """Load documents from the backend safely."""
    try:
        return list_documents()
    except Exception as exc:  # noqa: BLE001
        show_backend_error(exc, "Loading documents")
        return []


# -------------------------------------------------------------------
# Upload UI
# -------------------------------------------------------------------


def render_upload_section() -> None:
    """Render the document upload section."""
    st.subheader("📤 Upload notes")

    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT file",
        type=["pdf", "txt"],
        help="Upload your study notes to index them with StudyBuddy.",
    )

    if uploaded_file is None:
        return

    st.caption(
        f"Selected: **{uploaded_file.name}** "
        f"({uploaded_file.size / 1024:.1f} KB)"
    )

    if not st.button(
        "⬆️ Upload & Index",
        use_container_width=True,
        type="primary",
    ):
        return

    suffix = os.path.splitext(uploaded_file.name)[1]

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_path = temp_file.name

        with st.spinner("Indexing your notes..."):
            result = ingest_file(temp_path)

        st.success(
            f"Uploaded **{result['name']}** "
            f"with **{result['chunks']} chunks**."
        )

        st.session_state.messages = []
        st.rerun()

    except Exception as exc:  # noqa: BLE001
        show_backend_error(exc, "Upload")

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# -------------------------------------------------------------------
# Document selector
# -------------------------------------------------------------------


def render_document_selector(documents: list[dict]) -> None:
    """Render document selection and deletion controls."""
    st.subheader("📚 Your documents")

    if not documents:
        st.info("No documents uploaded yet.")
        st.session_state.selected_doc_id = None
        return

    names = [document["name"] for document in documents]

    current_id = st.session_state.get("selected_doc_id")

    current_index = 0

    for index, document in enumerate(documents):
        if document["doc_id"] == current_id:
            current_index = index
            break

    selected_name = st.selectbox(
        "Select a document",
        options=names,
        index=current_index,
    )

    selected_document = next(
        document
        for document in documents
        if document["name"] == selected_name
    )

    new_doc_id = selected_document["doc_id"]

    if new_doc_id != st.session_state.selected_doc_id:
        st.session_state.selected_doc_id = new_doc_id
        st.session_state.messages = []
        st.session_state.quiz_data = []
        st.session_state.flashcards = []
        st.session_state.flashcard_index = 0
        st.session_state.flashcard_flipped = False

    st.caption(f"Selected: **{selected_name}**")

    st.divider()

    if st.button(
        "🗑️ Delete selected document",
        use_container_width=True,
    ):
        try:
            with st.spinner("Deleting document..."):
                deleted = delete_document(new_doc_id)

            if deleted:
                st.success("Document deleted.")
                st.session_state.selected_doc_id = None
                st.session_state.messages = []
                st.session_state.quiz_data = []
                st.session_state.flashcards = []
                st.rerun()
            else:
                st.warning("The document could not be deleted.")

        except Exception as exc:  # noqa: BLE001
            show_backend_error(exc, "Delete")


# -------------------------------------------------------------------
# About section
# -------------------------------------------------------------------


def render_about() -> None:
    """Render project information in the sidebar."""
    st.divider()

    with st.expander("ℹ️ About StudyBuddy"):
        st.markdown(
            """
            **StudyBuddy** is an offline AI study assistant.

            - 📄 Upload PDF/TXT notes
            - 💬 Ask questions about your notes
            - 📝 Generate summaries
            - 🧠 Practice with quizzes
            - 🗂️ Review flashcards
            - 🔒 Runs locally with Ollama

            **Model:** Gemma 3 4B  
            **Embeddings:** nomic-embed-text  
            **License:** MIT
            """
        )


# -------------------------------------------------------------------
# Chat
# -------------------------------------------------------------------


def render_sources(sources: list[dict]) -> None:
    """Render answer sources."""
    if not sources:
        return

    with st.expander("📚 Sources"):
        for source in sources:
            st.markdown(
                f"**{source.get('file', 'Unknown file')}** — "
                f"Page {source.get('page', 'N/A')}"
            )
            st.caption(source.get("snippet", ""))


def render_chat() -> None:
    """Render the chat interface."""
    st.subheader("💬 Chat with your notes")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                render_sources(message["sources"])

    question = st.chat_input(
        "Ask a question about your notes..."
    )

    if not question:
        return

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
                doc_id=st.session_state.selected_doc_id,
                top_k=4,
                history=history,
            )

            answer = response.get(
                "answer",
                "I could not generate an answer.",
            )

            sources = response.get("sources", [])

            st.markdown(answer)
            render_sources(sources)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                }
            )

        except TypeError:
            # Backward compatibility if an older backend does not
            # yet accept the optional history parameter.
            try:
                response = ask(
                    question,
                    doc_id=st.session_state.selected_doc_id,
                    top_k=4,
                )

                answer = response.get(
                    "answer",
                    "I could not generate an answer.",
                )

                sources = response.get("sources", [])

                st.markdown(answer)
                render_sources(sources)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

            except Exception as exc:  # noqa: BLE001
                error_message = f"Unable to answer: {exc}"
                show_backend_error(exc, "Chat")
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )

        except Exception as exc:  # noqa: BLE001
            error_message = f"Unable to answer: {exc}"
            show_backend_error(exc, "Chat")

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )


# -------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------


def render_summary() -> None:
    """Render the document summary tab."""
    st.subheader("📝 Summary")

    if st.button(
        "✨ Generate summary",
        type="primary",
        use_container_width=True,
    ):
        try:
            with st.spinner("Generating summary..."):
                summary = summarize(
                    st.session_state.selected_doc_id
                )

            st.markdown(summary)

        except Exception as exc:  # noqa: BLE001
            show_backend_error(exc, "Summary")


# -------------------------------------------------------------------
# Quiz
# -------------------------------------------------------------------


def render_quiz() -> None:
    """Render interactive multiple-choice quiz."""
    st.subheader("🧠 Quiz")

    col1, col2 = st.columns([3, 1])

    with col1:
        quiz_count = st.slider(
            "Number of questions",
            min_value=3,
            max_value=10,
            value=5,
        )

    with col2:
        st.write("")
        st.write("")
        generate_clicked = st.button(
            "🎯 Generate",
            type="primary",
            use_container_width=True,
        )

    if generate_clicked:
        try:
            with st.spinner("Creating your quiz..."):
                quiz = generate_quiz(
                    st.session_state.selected_doc_id,
                    n=quiz_count,
                )

            st.session_state.quiz_data = quiz
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.rerun()

        except Exception as exc:  # noqa: BLE001
            show_backend_error(exc, "Quiz generation")
            return

    quiz = st.session_state.quiz_data

    if not quiz:
        st.info("Generate a quiz to start practicing.")
        return

    for index, item in enumerate(quiz):
        st.markdown(
            f"### Question {index + 1}"
        )
        st.write(item["question"])

        answer = st.radio(
            "Choose an answer:",
            options=item["options"],
            key=f"quiz_question_{index}",
            index=None,
        )

        st.session_state.quiz_answers[index] = answer

    if st.button(
        "✅ Check answers",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.quiz_submitted = True

    if not st.session_state.quiz_submitted:
        return

    score = 0

    for index, item in enumerate(quiz):
        selected_answer = st.session_state.quiz_answers.get(index)

        if selected_answer is None:
            st.warning(f"Question {index + 1}: not answered.")
            continue

        correct_index = item["answer_index"]

        if (
            0 <= correct_index < len(item["options"])
            and selected_answer == item["options"][correct_index]
        ):
            score += 1
            st.success(f"Question {index + 1}: Correct! ✅")
        else:
            correct_answer = item["options"][correct_index]
            st.error(
                f"Question {index + 1}: Incorrect. "
                f"Correct answer: **{correct_answer}**"
            )

        st.caption(
            f"Explanation: {item.get('explanation', 'No explanation provided.')}"
        )

    total = len(quiz)

    st.markdown(
        f"""
        <div class="score-card">
            <h2>🏆 Your Score</h2>
            <h1>{score}/{total}</h1>
            <p>{(score / total) * 100:.0f}%</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------------
# Flashcards
# -------------------------------------------------------------------


def make_flashcard_csv(cards: list[dict]) -> bytes:
    """Convert flashcards to a downloadable CSV."""
    output = io.StringIO()

    writer = csv.writer(output)
    writer.writerow(["Front", "Back"])

    for card in cards:
        writer.writerow(
            [
                card.get("front", ""),
                card.get("back", ""),
            ]
        )

    return output.getvalue().encode("utf-8")


def render_flashcards() -> None:
    """Render interactive flashcards."""
    st.subheader("🗂️ Flashcards")

    col1, col2 = st.columns([3, 1])

    with col1:
        flashcard_count = st.slider(
            "Number of flashcards",
            min_value=5,
            max_value=20,
            value=10,
        )

    with col2:
        st.write("")
        st.write("")
        generate_clicked = st.button(
            "🧠 Generate",
            type="primary",
            use_container_width=True,
        )

    if generate_clicked:
        try:
            with st.spinner("Creating flashcards..."):
                cards = generate_flashcards(
                    st.session_state.selected_doc_id,
                    n=flashcard_count,
                )

            st.session_state.flashcards = cards
            st.session_state.flashcard_index = 0
            st.session_state.flashcard_flipped = False
            st.rerun()

        except Exception as exc:  # noqa: BLE001
            show_backend_error(exc, "Flashcard generation")
            return

    cards = st.session_state.flashcards

    if not cards:
        st.info("Generate flashcards to start reviewing.")
        return

    index = st.session_state.flashcard_index
    card = cards[index]

    st.caption(
        f"Card {index + 1} of {len(cards)}"
    )

    if st.session_state.flashcard_flipped:
        st.markdown(
            f"""
            <div class="feature-card">
                <h3>Answer</h3>
                <p>{card.get("back", "")}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="feature-card">
                <h3>Question</h3>
                <p>{card.get("front", "")}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button(
        "🔄 Flip card",
        use_container_width=True,
    ):
        st.session_state.flashcard_flipped = (
            not st.session_state.flashcard_flipped
        )
        st.rerun()

    previous_col, next_col = st.columns(2)

    with previous_col:
        if st.button(
            "⬅️ Previous",
            use_container_width=True,
            disabled=index == 0,
        ):
            st.session_state.flashcard_index -= 1
            st.session_state.flashcard_flipped = False
            st.rerun()

    with next_col:
        if st.button(
            "Next ➡️",
            use_container_width=True,
            disabled=index == len(cards) - 1,
        ):
            st.session_state.flashcard_index += 1
            st.session_state.flashcard_flipped = False
            st.rerun()

    st.download_button(
        "⬇️ Download Flashcards as CSV",
        data=make_flashcard_csv(cards),
        file_name="studybuddy_flashcards.csv",
        mime="text/csv",
        use_container_width=True,
    )


# -------------------------------------------------------------------
# Main application
# -------------------------------------------------------------------


def main() -> None:
    """Run the StudyBuddy Streamlit application."""
    load_css()
    initialize_state()

    with st.sidebar:
        st.title("📚 StudyBuddy")
        st.caption("Your offline AI study assistant")

        st.divider()

        render_upload_section()

        st.divider()

        documents = get_documents()
        render_document_selector(documents)

        render_about()

    st.markdown(
        '<div class="studybuddy-title">StudyBuddy 📚</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="studybuddy-subtitle">'
        "Chat with your study notes using offline AI."
        "</div>",
        unsafe_allow_html=True,
    )

    selected_doc_id = st.session_state.get("selected_doc_id")

    if not selected_doc_id:
        st.info(
            "📄 Upload a PDF or TXT file from the sidebar "
            "to start studying."
        )

        st.markdown(
            """
            ### What you can do

            | Feature | Description |
            |---|---|
            | 💬 Chat | Ask questions about your notes |
            | 📝 Summary | Generate a concise summary |
            | 🧠 Quiz | Test yourself with MCQs |
            | 🗂️ Flashcards | Review and download flashcards |
            """
        )

        return

    st.success(
        "Document selected. Ask anything about your notes! 📖"
    )

    chat_tab, summary_tab, quiz_tab, flashcard_tab = st.tabs(
        [
            "💬 Chat",
            "📝 Summary",
            "🧠 Quiz",
            "🗂️ Flashcards",
        ]
    )

    with chat_tab:
        render_chat()

    with summary_tab:
        render_summary()

    with quiz_tab:
        render_quiz()

    with flashcard_tab:
        render_flashcards()


if __name__ == "__main__":
    main()