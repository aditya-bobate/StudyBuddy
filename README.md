# StudyBuddy

StudyBuddy is an open-source, fully offline AI study assistant powered by local LLMs. Upload your study notes, ask questions, generate summaries, quizzes, and flashcards—all without sending your data to the cloud.

## Features

- **Document Ingestion**: Upload PDF or TXT study notes securely.
- **RAG QA**: Ask questions and get answers grounded directly in your documents.
- **Source Citations**: Verify answers with specific snippets and page numbers.
- **Auto-Summarization**: Instantly generate overviews of dense material.
- **Smart Quizzes**: Generate multiple-choice quizzes to test your knowledge.
- **Flashcards**: Automatically create study flashcards from key concepts.
- **100% Offline & Private**: Uses Ollama to run models locally on your hardware.

## Architecture

StudyBuddy uses a modern, modular Python stack:
- **Frontend**: Streamlit for a fast, responsive UI.
- **Backend**: Python 3.10 API layer.
- **Vector Database**: ChromaDB for fast semantic search.
- **Embeddings**: `nomic-embed-text` for document chunk vectorization.
- **LLM Engine**: `gemma3:4b` running via Ollama.

## Requirements

- Windows 10/11
- Python 3.10+
- Ollama
- `gemma3:4b` and `nomic-embed-text` models in Ollama

## Installation

### Windows Setup

1. **Install Ollama**
   Download and install Ollama from [ollama.com](https://ollama.com).

2. **Clone the Repository**
   ```bash
   git clone <your-repo-url>
   cd StudyBuddy
   ```

3. **Run the Setup Script**
   StudyBuddy includes automated setup scripts that configure the environment and download required models:
   ```powershell
   .\setup.ps1
   ```
   *Alternatively, use `setup.bat` or `setup.sh` depending on your OS.*

## Usage

1. **Start Ollama** (if not already running in the background)
2. **Activate the Environment**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
3. **Run the App**
   ```bash
   streamlit run app/app.py
   ```

### Demo Instructions
*(GIF Placeholder)*
See [docs/DEMO.md](docs/DEMO.md) for full demo instructions.

## API Contract

The backend uses a strict API contract located in `backend/api.py`.
- `ingest_file(path: str) -> dict`
- `list_documents() -> list[dict]`
- `ask(question: str, doc_id: str, ...) -> dict`
- `summarize(doc_id: str) -> str`
- `generate_quiz(doc_id: str, n: int) -> list[dict]`
- `generate_flashcards(doc_id: str, n: int) -> list[dict]`

## Testing

Run tests via `pytest`:
```bash
python -m pytest tests/
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on our branching strategy, issue-first workflow, and review processes.

## License

MIT License. Note that the AI models retain their respective licenses and terms of use (e.g., Google's Gemma terms).
