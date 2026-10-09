# 📚 StudyBuddy — Your Personal AI Study Space

**Turn your study notes into answers, summaries, quizzes, and flashcards with locally running AI.**

StudyBuddy is an AI-powered study assistant built with Python and Streamlit. Upload your PDF or TXT notes, ask questions about the material, generate revision summaries, practise multiple-choice quizzes, and create flashcards—all through a clean, modern interface.

The application uses Ollama to run language and embedding models locally, with ChromaDB for document storage and semantic retrieval.

## ✨ Features

- **Document Upload:** Import PDF and TXT study notes.
- **AI Study Chat:** Ask questions about uploaded material and view supporting source snippets with file and page information.
- **Smart Summaries:** Generate concise revision notes from a selected document.
- **Interactive Quizzes:** Create multiple-choice questions with four options, answer checking, and explanations.
- **Flashcard Studio:** Generate question-and-answer cards, reveal answers, and export your deck.
- **Document Library:** View, select, and delete stored documents.
- **Modern Interface:** Dark theme, gradient styling, responsive layout, and dedicated study-tool tabs.
- **Local AI:** Run generation and embedding models through your local Ollama service.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application and backend logic |
| Streamlit | Interactive web interface |
| Ollama | Local language-model and embedding-model runtime |
| Gemma 3 4B | Answer generation, summaries, quizzes, and flashcards |
| nomic-embed-text | Text embeddings for semantic retrieval |
| ChromaDB | Vector storage and similarity search |
| pypdf | PDF text extraction |
| pytest | Automated tests |
| Ruff | Linting and code formatting |

## 🏗️ Architecture

1. **Upload:** The user imports a study document.
2. **Extract and chunk:** The backend extracts text, keeps page information, and splits the text into chunks.
3. **Embed and store:** The embedding model transforms chunks into vectors stored in ChromaDB.
4. **Retrieve:** When the user asks a question, relevant chunks are retrieved from the document collection.
5. **Generate:** Ollama generates a response using the retrieved context, or creates a summary, quiz, or flashcard deck.
6. **Display:** Streamlit presents the result in the study workspace.

## 📁 Project Structure

```text
StudyBuddy/
├── app/
│   └── app.py
├── backend/
│   ├── api.py
│   ├── errors.py
│   ├── ingest.py
│   ├── llm.py
│   ├── quiz.py
│   └── rag.py
├── tests/
│   ├── test_api_contract.py
│   └── test_integration.py
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or a compatible Python version
- [Ollama](https://ollama.com/)
- Sufficient disk space and memory for the selected local models

### 1. Clone the repository

```bash
git clone https://github.com/aditya-bobate/StudyBuddy.git
cd StudyBuddy
```

### 2. Create and activate a virtual environment

**macOS / Linux**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Download the required models

```bash
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

Ensure the Ollama service is running before starting the application.

### 5. Run StudyBuddy

```bash
python -m streamlit run app/app.py
```

Open the local URL displayed by Streamlit, typically `http://localhost:8501`.

### 6. Start studying

Upload a PDF or TXT file from the sidebar, select it from your library, and use the Chat, Summary, Quiz, and Flashcards tabs.

## 🧪 Testing and Code Quality

Run the automated test suite:

```bash
python -m pytest tests/ -q
```

Run the linter:

```bash
ruff check .
```

Format the code when needed:

```bash
ruff format .
```

Tests that require Ollama must be run with Ollama available. The CI environment should skip tests that depend on a local Ollama service when that service is unavailable.

## 🔒 Privacy and Data

StudyBuddy is designed around local AI processing. Once the models are downloaded, prompts and document processing can use your local Ollama service rather than a hosted AI API.

- Documents and vector data are stored locally by default.
- The ChromaDB storage location can be configured with `STUDYBUDDY_CHROMA_PATH`.
- Model downloads and Python package installation require internet access.
- Protect your local documents, database, and any sensitive material as you would other files on your computer.

The default local configuration is not automatically a public cloud deployment. A hosted deployment needs an appropriate model runtime, storage configuration, and resource allocation.

## 🗺️ Future Improvements

- Improved document organization and search
- Study progress tracking and learning statistics
- More quiz modes and spaced-repetition flashcards
- Better handling of scanned PDFs with optional OCR
- Automated CI checks and expanded test coverage
- Deployment configuration for a suitable hosted environment

## 👨‍💻 Author

**Yug Gandhi**

Built as a project to explore local language models, retrieval-augmented generation, vector databases, and AI-assisted learning.

## 📄 License

Add a license before redistributing this project publicly. Until a license is included, do not assume others have permission to reuse the code.
