# StudyBuddy

StudyBuddy is an open-source, fully offline AI study assistant powered by local LLMs. Upload your study notes, ask questions, generate summaries, quizzes, and flashcards — all without sending your study documents to a cloud LLM.

## Features

- **Document Ingestion** — Upload PDF or TXT study notes.
- **RAG Question Answering** — Ask questions and get answers grounded in your documents.
- **Source Citations** — Verify answers using source snippets and page numbers.
- **Auto-Summarization** — Generate concise summaries of study material.
- **Smart Quizzes** — Generate multiple-choice quizzes from documents.
- **Flashcards** — Automatically create flashcards from key concepts.
- **Offline & Private** — Uses Ollama to run supported models locally.

## Architecture

StudyBuddy uses a modular Python stack:

- **Frontend:** Streamlit
- **Backend:** Python 3.10+
- **Vector Database:** ChromaDB
- **Embeddings:** `nomic-embed-text`
- **LLM Engine:** Ollama with `gemma3:4b`

See [docs/architecture.md](docs/architecture.md) for the project architecture.

## Requirements

- Windows 10/11
- Python 3.10+
- Ollama
- `gemma3:4b` Ollama model
- `nomic-embed-text` Ollama model

## Installation

### Windows Setup

#### 1. Install Ollama

Install Ollama from [ollama.com](https://ollama.com).

#### 2. Clone the Repository

```powershell
git clone https://github.com/aditya-bobate/StudyBuddy.git
cd StudyBuddy
```

#### 3. Run the Setup Script

```powershell
.\setup.ps1
```

Alternatively, you can use:

```text
setup.bat
```

or:

```text
setup.sh
```

on compatible Unix-like systems.

#### 4. Configure Environment Variables

Copy `.env.example` to `.env` and adjust the values if required.

### Required Ollama Models

Make sure the required models are available locally:

```powershell
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

After the required models are downloaded, StudyBuddy can perform supported document processing and inference locally without sending study documents to a cloud LLM.

## Usage

### 1. Start Ollama

Start Ollama if it is not already running.

### 2. Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Start the Application

```powershell
streamlit run app/app.py
```

Open the local Streamlit URL shown in the terminal.

## API Contract

The backend exposes a stable API contract through `backend/api.py`.

The current implementation contains deterministic stubs so the frontend can be developed independently of the AI backend.

### `ingest_file`

```python
ingest_file(path: str) -> dict
```

Returns:

```json
{
  "doc_id": "string",
  "name": "string",
  "chunks": 42
}
```

### `list_documents`

```python
list_documents() -> list[dict]
```

Returns:

```json
[
  {
    "doc_id": "string",
    "name": "string"
  }
]
```

### `ask`

```python
ask(
    question: str,
    doc_id: str | None = None,
    top_k: int = 4,
    history: list[dict] | None = None
) -> dict
```

Returns:

```json
{
  "answer": "string",
  "sources": [
    {
      "file": "string",
      "page": 1,
      "snippet": "string"
    }
  ]
}
```

The `page` value may be `null` when a source does not have a page number.

### `summarize`

```python
summarize(doc_id: str) -> str
```

Returns a summary string.

### `generate_quiz`

```python
generate_quiz(doc_id: str, n: int = 5) -> list[dict]
```

Each quiz item contains:

```json
{
  "question": "string",
  "options": [
    "string",
    "string",
    "string",
    "string"
  ],
  "answer_index": 0,
  "explanation": "string"
}
```

`answer_index` is zero-based and must be between `0` and `3`.

### `generate_flashcards`

```python
generate_flashcards(doc_id: str, n: int = 10) -> list[dict]
```

Each flashcard contains:

```json
{
  "front": "string",
  "back": "string"
}
```

### `delete_document`

```python
delete_document(doc_id: str) -> bool
```

Returns a boolean indicating whether the deletion succeeded.

> These contracts are intentionally stable so the Streamlit frontend can be developed independently of the AI implementation.

## Project Structure

```text
StudyBuddy/
├── app/
│   ├── app.py
│   └── components/
├── backend/
│   ├── __init__.py
│   ├── api.py
│   ├── errors.py
│   ├── ingest.py
│   ├── llm.py
│   ├── quiz.py
│   └── rag.py
├── docs/
│   ├── architecture.md
│   └── DEMO.md
├── sample_data/
│   └── biology_notes.txt
├── tests/
│   ├── test_api_contract.py
│   └── test_integration.py
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── pull_request_template.md
│   └── workflows/
├── .env.example
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── requirements.txt
├── setup.bat
├── setup.ps1
└── setup.sh
```

## Testing

Run the complete test suite:

```powershell
python -m pytest -v
```

The integration test requires Ollama to be running. If Ollama is unavailable, the integration test is skipped automatically.

Run only the API contract tests:

```powershell
python -m pytest tests/test_api_contract.py -v
```

## Sample Data

A small original biology study-notes file is included at:

```text
sample_data/biology_notes.txt
```

It can be used to test document ingestion and the application workflow without requiring external study material.

## Demo

See [docs/DEMO.md](docs/DEMO.md) for the recommended demonstration flow.

## Contributing

Contributions are welcome.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue or pull request.

The project follows an issue-first workflow with feature branches, pull requests, CI checks, and peer review.

## Privacy

StudyBuddy is designed around local processing.

Once the required models are downloaded, supported document processing and model inference can run locally through Ollama. Study documents are not intentionally uploaded to a cloud LLM by StudyBuddy.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

The AI models used by StudyBuddy retain their respective licenses and terms of use. For example, Gemma has its own model license and terms.