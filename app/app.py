
import os
import tempfile
from pathlib import Path

import streamlit as st

from backend.api import (
    ask,
    delete_document,
    generate_flashcards,
    generate_quiz,
    ingest_file,
    list_documents,
    summarize,
)

st.set_page_config(
    page_title="StudyBuddy — Your AI Study Space",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# DESIGN SYSTEM
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #080910;
    --panel: #10121e;
    --panel2: #151827;
    --border: rgba(174,160,255,.14);
    --muted: #9297ad;
    --white: #f5f5ff;
    --purple: #a78bfa;
    --cyan: #67e8f9;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
      radial-gradient(ellipse at 10% 0%, rgba(101,61,180,.14), transparent 35%),
      radial-gradient(ellipse at 95% 25%, rgba(27,146,180,.08), transparent 30%),
      var(--bg);
    color: var(--white);
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111321 0%, #0b0c15 100%);
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}

h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -.6px;
    color: #f7f6ff;
}

p, label, .stCaption {
    color: #c1c4d6;
}

.hero {
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(180,155,255,.23);
    border-radius: 25px;
    padding: 34px 35px;
    margin: 8px 0 24px 0;
    background:
      radial-gradient(ellipse at 90% 10%, rgba(103,232,249,.14), transparent 35%),
      radial-gradient(ellipse at 15% 100%, rgba(167,139,250,.24), transparent 55%),
      linear-gradient(125deg, #17152b 0%, #111322 55%, #101c29 100%);
    box-shadow: 0 20px 70px rgba(0,0,0,.18);
}

.hero-kicker {
    color: #c4b5fd;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 15px;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(30px, 4vw, 49px);
    line-height: 1.12;
    font-weight: 700;
    letter-spacing: -2px;
    margin: 0;
    color: white;
}

.gradient-text {
    background: linear-gradient(95deg, #c4b5fd 5%, #a5f3fc 90%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-sub {
    color: #b9bdd2;
    font-size: 15px;
    line-height: 1.7;
    max-width: 600px;
    margin-top: 15px;
}

.pill {
    display: inline-block;
    border: 1px solid rgba(167,139,250,.3);
    color: #ddd6fe;
    background: rgba(139,92,246,.10);
    border-radius: 30px;
    padding: 7px 12px;
    font-size: 11px;
    margin-bottom: 18px;
}

.section-label {
    color: #aaa6c8;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    margin: 24px 0 12px;
}

.panel {
    background: linear-gradient(145deg, rgba(24,27,43,.94), rgba(15,17,29,.97));
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 14px;
    transition: border-color .2s ease, transform .2s ease;
}

.panel:hover {
    border-color: rgba(167,139,250,.35);
}

.stat-card {
    border: 1px solid var(--border);
    background: linear-gradient(145deg, rgba(27,29,47,.95), rgba(15,17,29,.95));
    border-radius: 17px;
    padding: 19px;
    min-height: 115px;
}

.stat-label {
    font-size: 12px;
    color: #9ea3bb;
    margin-bottom: 13px;
}

.stat-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 28px;
    color: white;
    font-weight: 700;
}

.stat-icon {
    float: right;
    font-size: 20px;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #191b2c, #10121d);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px;
}

div[data-testid="stMetricLabel"] {
    color: #a8aec4;
}

div[data-testid="stMetricValue"] {
    color: #f5f3ff;
    font-family: 'Space Grotesk', sans-serif;
}

.stButton > button {
    border-radius: 11px;
    border: 1px solid rgba(167,139,250,.22);
    background: linear-gradient(110deg, #8b5cf6, #6d5ce8);
    color: white;
    font-weight: 600;
    min-height: 43px;
    transition: all .2s ease;
}

.stButton > button:hover {
    border-color: #c4b5fd;
    box-shadow: 0 0 25px rgba(139,92,246,.22);
    transform: translateY(-1px);
    color: white;
}

.stButton > button[kind="secondary"] {
    background: #171929;
    border-color: var(--border);
    color: #ddd9f5;
}

.stTextInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input {
    background: #10121f !important;
    color: #f5f5ff !important;
    border-color: rgba(174,160,255,.2) !important;
    border-radius: 11px !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 10px 10px 0 0;
    color: #aeb2c9;
    padding: 13px 17px;
}

.stTabs [aria-selected="true"] {
    color: #d9ccff !important;
    border-bottom: 2px solid #a78bfa !important;
}

div[data-testid="stFileUploader"] {
    background: rgba(139,92,246,.045);
    border: 1px dashed rgba(167,139,250,.45);
    border-radius: 15px;
    padding: 12px;
}

div[data-testid="stFileUploader"] section {
    background: transparent;
}

div[data-testid="stChatMessage"] {
    background: rgba(22,24,39,.8);
    border: 1px solid var(--border);
    border-radius: 16px;
    margin-bottom: 12px;
}

.stAlert {
    border-radius: 12px;
}

hr {
    border-color: var(--border);
}

.sidebar-brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 25px;
    font-weight: 700;
    letter-spacing: -1px;
    margin: 6px 0 3px;
}

.sidebar-sub {
    color: #959bb3;
    font-size: 12px;
    line-height: 1.7;
    margin-bottom: 24px;
}

.doc-item {
    background: #151727;
    border: 1px solid var(--border);
    padding: 12px;
    border-radius: 12px;
    color: #e8e6fa;
    font-size: 13px;
    overflow-wrap: anywhere;
    margin: 8px 0;
}

.source-card {
    border: 1px solid rgba(103,232,249,.2);
    border-left: 3px solid #67e8f9;
    border-radius: 10px;
    background: rgba(103,232,249,.045);
    padding: 13px;
    margin: 9px 0;
    color: #cdd4e9;
    font-size: 13px;
    line-height: 1.6;
}

.empty-state {
    text-align: center;
    padding: 35px 20px;
    background: rgba(20,22,36,.65);
    border: 1px dashed rgba(167,139,250,.25);
    border-radius: 17px;
}

.empty-icon {
    font-size: 35px;
    margin-bottom: 12px;
}

.empty-title {
    color: #f4f1ff;
    font-size: 18px;
    font-weight: 700;
}

.empty-copy {
    color: #989eb7;
    font-size: 13px;
    line-height: 1.7;
    margin-top: 7px;
}

.flashcard {
    min-height: 130px;
    background: linear-gradient(145deg, #201b3b, #14182a);
    border: 1px solid rgba(167,139,250,.3);
    border-radius: 17px;
    padding: 22px;
    margin-bottom: 12px;
}

.flashcard-front {
    color: #ddd6fe;
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.flashcard-back {
    color: #d4d9ec;
    font-size: 14px;
    line-height: 1.7;
}

div[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #8b5cf6, #67e8f9);
}

@media (max-width: 768px) {
    .block-container { padding: 1rem 1rem 3rem; }
    .hero { padding: 24px 20px; }
    .hero-title { letter-spacing: -1px; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────

defaults = {
    "selected_doc": None,
    "chat_history": [],
    "last_summary": None,
    "last_quiz": None,
    "last_flashcards": None,
    "quiz_answers": {},
    "quiz_submitted": False,
    "flash_revealed": set(),
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_documents():
    try:
        return list_documents()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Could not load documents: {exc}")
        return []


def selected_document(docs):
    if not docs:
        return None

    ids = [doc["doc_id"] for doc in docs]
    current = st.session_state.selected_doc

    if current not in ids:
        st.session_state.selected_doc = ids[0]

    return next(
        (doc for doc in docs if doc["doc_id"] == st.session_state.selected_doc),
        docs[0],
    )


def clear_document_state():
    st.session_state.chat_history = []
    st.session_state.last_summary = None
    st.session_state.last_quiz = None
    st.session_state.last_flashcards = None
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False
    st.session_state.flash_revealed = set()


def render_empty(icon, title, copy):
    st.markdown(
        f"""
        <div class="empty-state">
          <div class="empty-icon">{icon}</div>
          <div class="empty-title">{title}</div>
          <div class="empty-copy">{copy}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(sources):
    if not sources:
        return

    with st.expander(f"📎 Sources used ({len(sources)})"):
        for source in sources:
            file_name = source.get("file", "Document")
            page = source.get("page", "?")
            snippet = source.get("snippet", "")

            st.markdown(
                f"""
                <div class="source-card">
                  <strong>📄 {file_name}</strong> · Page {page}<br>
                  {snippet}
                </div>
                """,
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">📚 Study<span style="color:#a78bfa">Buddy</span></div>
        <div class="sidebar-sub">YOUR PERSONAL AI STUDY SPACE<br>
        <span style="color:#67e8f9">●</span> LOCAL AI · PRIVATE BY DESIGN</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### ✦ Add study material")
    st.caption("Upload your notes to start learning with AI.")

    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT file",
        type=["pdf", "txt"],
        help="Supported formats: PDF and TXT",
        key="studybuddy_uploader",
    )

    if uploaded_file is not None:  # noqa: SIM102
        if st.button("＋  Import document", use_container_width=True):
            suffix = Path(uploaded_file.name).suffix.lower()
            temp_path = None

            try:
                with tempfile.NamedTemporaryFile(
                    suffix=suffix, delete=False
                ) as temp:
                    temp.write(uploaded_file.getvalue())
                    temp_path = temp.name

                with st.spinner("Processing your notes..."):
                    result = ingest_file(temp_path)

                st.session_state.selected_doc = result["doc_id"]
                clear_document_state()
                st.success(
                    f"Imported {result.get('name', uploaded_file.name)}"
                )
                st.rerun()

            except Exception as exc:  # noqa: BLE001
                st.error(f"Import failed: {exc}")

            finally:
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)

    st.markdown("---")
    st.markdown("### ◈ Your library")

    docs = get_documents()
    doc = selected_document(docs)

    if docs:
        labels = {
            item["doc_id"]: item["name"]
            for item in docs
        }

        current_id = st.session_state.selected_doc

        selected_id = st.selectbox(
            "Active document",
            options=list(labels.keys()),
            format_func=lambda value: labels[value],
            index=list(labels.keys()).index(current_id),
            key="active_document_selector",
        )

        if selected_id != st.session_state.selected_doc:
            st.session_state.selected_doc = selected_id
            clear_document_state()
            st.rerun()

        st.markdown(
            f'<div class="doc-item">📄 {labels[selected_id]}<br>'
            '<span style="color:#67e8f9;font-size:11px">● READY TO STUDY</span></div>',
            unsafe_allow_html=True,
        )

        st.caption(f"{len(docs)} document(s) in your library")

        with st.expander("Manage documents"):
            delete_id = st.selectbox(
                "Choose document to delete",
                options=list(labels.keys()),
                format_func=lambda value: labels[value],
                key="delete_document_selector",
            )

            st.warning("Deletion removes the selected document from your library.")

            confirm_delete = st.checkbox(
                "I want to delete this document",
                key="confirm_delete",
            )

            if st.button(
                "🗑 Delete document",
                disabled=not confirm_delete,
                use_container_width=True,
            ):
                try:
                    with st.spinner("Deleting document..."):
                        deleted = delete_document(delete_id)

                    if deleted:
                        if st.session_state.selected_doc == delete_id:
                            st.session_state.selected_doc = None
                            clear_document_state()
                        st.success("Document deleted.")
                        st.rerun()
                    else:
                        st.error("Document was not found or could not be deleted.")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Delete failed: {exc}")

    else:
        render_empty(
            "📂",
            "Your library is empty",
            "Import a PDF or TXT file to get started.",
        )

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:11px;color:#777f9b;line-height:1.8">
        <strong style="color:#c4b5fd">STUDYBUDDY v1.0</strong><br>
        Powered by local AI<br>
        Your notes stay on your machine.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# MAIN HERO
# ─────────────────────────────────────────────

docs = get_documents()
doc = selected_document(docs)

st.markdown(
    """
    <div class="hero">
      <div class="hero-kicker">✦ YOUR INTELLIGENT STUDY COMPANION</div>
      <div class="hero-title">Make learning<br>
      <span class="gradient-text">feel effortless.</span></div>
      <div class="hero-sub">
        Your notes. Your AI. Your pace.
        Turn your study material into answers, summaries,
        quizzes and flashcards — all powered by local AI.
      </div>
      <div style="margin-top:22px">
        <span class="pill">✧ PRIVATE & LOCAL</span>
        &nbsp; <span class="pill">◈ DOCUMENT-AWARE AI</span>
        &nbsp; <span class="pill">⚡ BUILT FOR LEARNING</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Stats row
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""<div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-label">Documents in library</div>
        <div class="stat-value">{len(docs)}</div>
        </div>""",
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """<div class="stat-card">
        <div class="stat-icon">✨</div>
        <div class="stat-label">AI study tools</div>
        <div class="stat-value">04</div>
        </div>""",
        unsafe_allow_html=True,
    )

with c3:
    active_name = doc["name"] if doc else "None selected"
    st.markdown(
        f"""<div class="stat-card">
        <div class="stat-icon">◉</div>
        <div class="stat-label">Current study material</div>
        <div style="font-size:17px;font-weight:700;margin-top:7px;overflow-wrap:anywhere">
        {active_name}</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-label">✦ YOUR WORKSPACE</div>', unsafe_allow_html=True)

chat_tab, summary_tab, quiz_tab, cards_tab = st.tabs(
    ["✧  AI CHAT", "▤  SUMMARY", "◈  QUIZ", "▧  FLASHCARDS"]
)


# ─────────────────────────────────────────────
# AI CHAT
# ─────────────────────────────────────────────

with chat_tab:
    st.markdown("## 💬 Ask your notes")
    st.caption(
        "Ask questions about your selected document. "
        "Answers are generated from retrieved study material."
    )

    if not doc:
        render_empty(
            "✦",
            "Your AI study space is ready",
            "Upload a PDF or TXT document from the sidebar to begin.",
        )
    else:
        for index, message in enumerate(st.session_state.chat_history):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("sources"):
                    render_sources(message["sources"])

        question = st.chat_input(
            f"Ask anything about {doc['name']}...",
            key="study_question",
        )

        if question:
            st.session_state.chat_history.append(
                {"role": "user", "content": question}
            )

            with st.chat_message("user"):
                st.markdown(question)

            history = [
                {"role": item["role"], "content": item["content"]}
                for item in st.session_state.chat_history[:-1]
            ]

            with st.chat_message("assistant"):  # noqa: SIM117
                with st.spinner("✦ Thinking through your notes..."):
                    try:
                        result = ask(
                            question,
                            doc_id=doc["doc_id"],
                            top_k=4,
                            history=history,
                        )

                        answer = result.get("answer", "No answer was returned.")
                        sources = result.get("sources", [])

                        st.markdown(answer)
                        render_sources(sources)

                        st.session_state.chat_history.append(
                            {
                                "role": "assistant",
                                "content": answer,
                                "sources": sources,
                            }
                        )

                    except Exception as exc:  # noqa: BLE001
                        st.error(f"Couldn't answer that question: {exc}")


# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────

with summary_tab:
    st.markdown("## ▤ Smart summary")
    st.caption("Turn long notes into a focused revision guide.")

    if not doc:
        render_empty("▤", "Nothing to summarize yet", "Import your notes first.")
    else:
        a, b = st.columns([3, 1])

        with a:
            st.markdown(
                f'<div class="panel"><div style="color:#a78bfa;font-size:11px;'
                f'letter-spacing:1px">CURRENT DOCUMENT</div>'
                f'<div style="font-size:17px;font-weight:700;margin-top:8px">'
                f'📄 {doc["name"]}</div></div>',
                unsafe_allow_html=True,
            )

        with b:
            st.write("")
            st.write("")
            generate_summary = st.button(
                "✦ Generate summary",
                use_container_width=True,
            )

        if generate_summary:
            try:
                with st.spinner("Creating your revision guide..."):
                    st.session_state.last_summary = summarize(doc["doc_id"])
            except Exception as exc:  # noqa: BLE001
                st.error(f"Summary generation failed: {exc}")

        if st.session_state.last_summary:
            st.markdown('<div class="section-label">YOUR REVISION GUIDE</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="panel" style="line-height:1.9">',
                unsafe_allow_html=True,
            )
            st.markdown(st.session_state.last_summary)
            st.markdown("</div>", unsafe_allow_html=True)

            st.download_button(
                "↓ Download summary",
                data=st.session_state.last_summary,
                file_name="studybuddy_summary.md",
                mime="text/markdown",
            )
        else:
            render_empty(
                "✧",
                "Clarity starts here",
                "Generate a concise summary of the active document for faster revision.",
            )


# ─────────────────────────────────────────────
# QUIZ
# ─────────────────────────────────────────────

with quiz_tab:
    st.markdown("## ◈ Test your knowledge")
    st.caption("Generate multiple-choice questions from your study material.")

    if not doc:
        render_empty("◈", "Ready when you are", "Import a document to generate a quiz.")
    else:
        q1, q2 = st.columns([2, 1])

        with q1:
            quiz_count = st.select_slider(
                "Number of questions",
                options=[3, 5, 8, 10],
                value=5,
            )

        with q2:
            st.write("")
            create_quiz = st.button(
                "✦ Build my quiz",
                use_container_width=True,
            )

        if create_quiz:
            try:
                with st.spinner("Preparing your questions..."):
                    quiz = generate_quiz(doc["doc_id"], n=quiz_count)

                st.session_state.last_quiz = quiz
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.success(f"Created {len(quiz)} question(s).")

            except Exception as exc:  # noqa: BLE001
                st.error(f"Quiz generation failed: {exc}")

        quiz = st.session_state.last_quiz

        if quiz:
            st.markdown('<div class="section-label">YOUR PRACTICE SESSION</div>', unsafe_allow_html=True)

            for i, item in enumerate(quiz):
                st.markdown(
                    f'<div class="panel"><div style="color:#a78bfa;font-size:11px;'
                    f'letter-spacing:1px">QUESTION {i + 1:02d} / {len(quiz):02d}</div>'
                    f'<div style="font-size:17px;font-weight:600;margin-top:10px">'
                    f'{item["question"]}</div></div>',
                    unsafe_allow_html=True,
                )

                options = item.get("options", [])

                if len(options) != 4:
                    st.warning(f"Question {i + 1} does not have exactly four options.")
                    continue

                selected_answer = st.radio(
                    f"Choose your answer for question {i + 1}",
                    options=list(range(4)),
                    format_func=lambda value, opts=options: (
                        f"{chr(65 + value)}. {opts[value]}"
                    ),
                    index=st.session_state.quiz_answers.get(i),
                    key=f"quiz_{doc['doc_id']}_{i}",
                    label_visibility="collapsed",
                )

                st.session_state.quiz_answers[i] = selected_answer

                if st.session_state.quiz_submitted:
                    correct_index = item.get("answer_index")

                    if selected_answer == correct_index:
                        st.success("Correct answer!")
                    else:
                        st.error(
                            f"Correct answer: {options[correct_index]}"
                            if isinstance(correct_index, int)
                            and 0 <= correct_index < len(options)
                            else "Correct answer index is invalid."
                        )

                    explanation = item.get("explanation")
                    if explanation:
                        st.caption(f"Explanation: {explanation}")

            if not st.session_state.quiz_submitted:
                if st.button("✓ Submit answers", use_container_width=True):
                    st.session_state.quiz_submitted = True
                    st.rerun()
            else:
                valid_questions = [
                    item for item in quiz
                    if isinstance(item.get("answer_index"), int)
                    and 0 <= item["answer_index"] < len(item.get("options", []))
                ]
                score = sum(
                    st.session_state.quiz_answers.get(i) == item["answer_index"]
                    for i, item in enumerate(quiz)
                    if item in valid_questions
                )

                st.markdown(
                    f'<div class="panel" style="text-align:center">'
                    f'<div style="font-size:12px;color:#a78bfa;letter-spacing:2px">'
                    f'YOUR RESULT</div><div style="font-size:40px;font-weight:700;'
                    f'margin:10px 0">{score} / {len(quiz)}</div>'
                    f'<div style="color:#a8aec4">Keep going — every session counts.</div></div>',
                    unsafe_allow_html=True,
                )

                if st.button("↻ Try again"):
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.rerun()

        else:
            render_empty(
                "◈",
                "Practice makes progress",
                "Generate a quiz and see how well you understand your notes.",
            )


# ─────────────────────────────────────────────
# FLASHCARDS
# ─────────────────────────────────────────────

with cards_tab:
    st.markdown("## ▧ Flashcard studio")
    st.caption("Learn key concepts with question-and-answer cards.")

    if not doc:
        render_empty("▧", "No cards yet", "Import your study material to get started.")
    else:
        f1, f2 = st.columns([2, 1])

        with f1:
            card_count = st.select_slider(
                "Number of flashcards",
                options=[5, 10, 15, 20],
                value=10,
            )

        with f2:
            st.write("")
            make_cards = st.button(
                "✦ Create flashcards",
                use_container_width=True,
            )

        if make_cards:
            try:
                with st.spinner("Creating your study cards..."):
                    st.session_state.last_flashcards = generate_flashcards(
                        doc["doc_id"], n=card_count
                    )
                    st.session_state.flash_revealed = set()
            except Exception as exc:  # noqa: BLE001
                st.error(f"Flashcard generation failed: {exc}")

        cards = st.session_state.last_flashcards

        if cards:
            st.markdown(
                f'<div class="section-label">{len(cards)} STUDY CARDS · '
                f'ACTIVE DECK</div>',
                unsafe_allow_html=True,
            )

            cols = st.columns(2)

            for i, card in enumerate(cards):
                with cols[i % 2]:  # noqa: SIM117
                    with st.container(border=True):
                        st.markdown(
                            f'<div class="flashcard-front">CARD {i + 1:02d}</div>'
                            f'<div style="font-size:17px;font-weight:700;'
                            f'margin:10px 0 18px">{card["front"]}</div>',
                            unsafe_allow_html=True,
                        )

                        if i in st.session_state.flash_revealed:
                            st.markdown(
                                f'<div class="flashcard-back">'
                                f'{card["back"]}</div>',
                                unsafe_allow_html=True,
                            )

                            if st.button("Hide answer", key=f"hide_{i}_{doc['doc_id']}"):
                                st.session_state.flash_revealed.discard(i)
                                st.rerun()
                        else:
                            if st.button("Reveal answer ↗", key=f"reveal_{i}_{doc['doc_id']}"):
                                st.session_state.flash_revealed.add(i)
                                st.rerun()

            export_text = "\n\n".join(
                f"Q: {card['front']}\nA: {card['back']}"
                for card in cards
            )

            st.download_button(
                "↓ Export flashcards",
                data=export_text,
                file_name="studybuddy_flashcards.txt",
                mime="text/plain",
            )
        else:
            render_empty(
                "▧",
                "Build your memory deck",
                "Create flashcards from your notes and reveal answers as you practise.",
            )


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.markdown("---")
st.markdown(
    """
    <div style="text-align:center;padding:12px 0 4px;color:#727991;font-size:11px">
      MADE FOR DEEPER LEARNING &nbsp;·&nbsp;
      <span style="color:#a78bfa">STUDYBUDDY</span>
      &nbsp;·&nbsp; LOCAL AI, YOUR WAY
    </div>
    """,
    unsafe_allow_html=True,
)
