import json
import os
import re
import uuid

import chromadb
import ollama
from pypdf import PdfReader

from .errors import EmptyDocument, ModelMissing, OllamaNotRunning, UnsupportedFile

OLLAMA_HOST = "http://localhost:11434"
CHAT_MODEL = "gemma3:4b"
EMBED_MODEL = "nomic-embed-text"

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
REGISTRY_FILE = os.path.join(DATA_DIR, "documents.json")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma")

os.makedirs(DATA_DIR, exist_ok=True)

_client = chromadb.PersistentClient(path=CHROMA_DIR)
_collection = _client.get_or_create_collection(name="studybuddy")

_ollama = ollama.Client(host=OLLAMA_HOST)


def _check_ollama():
    try:
        models = _ollama.list()
        model_text = str(models)

        if CHAT_MODEL not in model_text:
            raise ModelMissing(
                f"Required model '{CHAT_MODEL}' is not installed."
            )

        if EMBED_MODEL not in model_text:
            raise ModelMissing(
                f"Required model '{EMBED_MODEL}' is not installed."
            )

    except ModelMissing:
        raise
    except Exception as exc:
        raise OllamaNotRunning(
            "Ollama is not running. Start Ollama and try again."
        ) from exc


def _load_registry():
    if not os.path.exists(REGISTRY_FILE):
        return {}

    try:
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_registry(registry):
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)


def _read_file(path):
    extension = os.path.splitext(path)[1].lower()

    if extension == ".pdf":
        reader = PdfReader(path)
        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append((page_number, text))

        return pages

    if extension == ".txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        return [(1, text)]

    raise UnsupportedFile(
        "Unsupported file type. StudyBuddy currently supports PDF and TXT."
    )


def _chunk_text(text, chunk_size=500, overlap=80):
    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def _embed(text):
    result = _ollama.embeddings(
        model=EMBED_MODEL,
        prompt=text,
    )
    return result["embedding"]


def _generate(prompt):
    response = _ollama.generate(
        model=CHAT_MODEL,
        prompt=prompt,
    )
    return response["response"].strip()


def _get_document_chunks(doc_id):
    result = _collection.get(
        where={"doc_id": doc_id},
        include=["documents", "metadatas"],
    )

    documents = result.get("documents") or []
    metadatas = result.get("metadatas") or []

    return list(zip(documents, metadatas))


def _extract_json(text):
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text)
        text = re.sub(r"```$", "", text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)

        if not match:
            raise

        return json.loads(match.group(1))


def ingest_file(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    pages = _read_file(path)

    if not pages or not any(text.strip() for _, text in pages):
        raise EmptyDocument("The document is empty.")

    _check_ollama()

    doc_id = str(uuid.uuid4())
    name = os.path.basename(path)

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    chunk_number = 0

    for page_number, page_text in pages:
        chunks = _chunk_text(page_text)

        for chunk in chunks:
            chunk_number += 1
            ids.append(f"{doc_id}-{chunk_number}")
            embeddings.append(_embed(chunk))
            documents.append(chunk)
            metadatas.append(
                {
                    "doc_id": doc_id,
                    "file": name,
                    "page": page_number,
                }
            )

    if not documents:
        raise EmptyDocument("No readable text was found in the document.")

    _collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    registry = _load_registry()
    registry[doc_id] = {
        "doc_id": doc_id,
        "name": name,
    }
    _save_registry(registry)

    return {
        "doc_id": doc_id,
        "name": name,
        "chunks": len(documents),
    }


def list_documents() -> list[dict]:
    registry = _load_registry()
    return list(registry.values())


def ask(
    question: str,
    doc_id: str | None = None,
    top_k: int = 4,
    history: list[dict] | None = None,
) -> dict:
    _check_ollama()

    if not question.strip():
        return {
            "answer": "Please enter a question.",
            "sources": [],
        }

    query_embedding = _embed(question)

    if doc_id:
        results = _collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"doc_id": doc_id},
        )
    else:
        results = _collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return {
            "answer": "I couldn't find any relevant content in the selected document.",
            "sources": [],
        }

    context_parts = []

    for index, (document, metadata) in enumerate(
        zip(documents, metadatas), start=1
    ):
        context_parts.append(
            f"[Source {index}]\n"
            f"File: {metadata.get('file', 'Unknown')}\n"
            f"Page: {metadata.get('page', 1)}\n"
            f"Content: {document}"
        )

    context = "\n\n".join(context_parts)

    history_text = ""

    if history:
        recent_history = history[-6:]
        history_text = "\n".join(
            f"{item.get('role', 'user')}: {item.get('content', '')}"
            for item in recent_history
        )

    prompt = f"""
You are StudyBuddy, an offline AI study assistant.

Answer the student's question using ONLY the provided document context.
If the answer is not present in the context, clearly say that the document
does not contain enough information.

Be accurate, concise, and student-friendly.

Previous conversation:
{history_text}

Document context:
{context}

Student question:
{question}

Answer:
"""

    answer = _generate(prompt)

    sources = []

    for document, metadata in zip(documents, metadatas):
        sources.append(
            {
                "file": metadata.get("file", "Unknown"),
                "page": int(metadata.get("page", 1)),
                "snippet": document[:500],
            }
        )

    return {
        "answer": answer,
        "sources": sources,
    }


def summarize(doc_id: str) -> str:
    _check_ollama()

    chunks = _get_document_chunks(doc_id)

    if not chunks:
        return "Document not found."

    context = "\n\n".join(
        document for document, _ in chunks
    )

    context = context[:30000]

    prompt = f"""
Create a clear study summary of the following document.

Include:
- Main topics
- Important concepts
- Key definitions
- Important points a student should remember

Use simple language and bullet points where useful.

Document:
{context}
"""

    return _generate(prompt)


def generate_quiz(doc_id: str, n: int = 5) -> list[dict]:
    _check_ollama()

    chunks = _get_document_chunks(doc_id)

    if not chunks:
        return []

    context = "\n\n".join(
        document for document, _ in chunks
    )[:30000]

    n = max(1, min(n, 20))

    prompt = f"""
Create {n} multiple-choice questions from the following study material.

Return ONLY valid JSON.
The JSON must be an array.
Each item must have exactly:
- question
- options: exactly 4 strings
- answer_index: integer from 0 to 3
- explanation

Study material:
{context}
"""

    raw = _generate(prompt)
    quiz = _extract_json(raw)

    if not isinstance(quiz, list):
        return []

    cleaned = []

    for item in quiz[:n]:
        if not isinstance(item, dict):
            continue

        options = item.get("options", [])

        if (
            isinstance(item.get("question"), str)
            and isinstance(options, list)
            and len(options) == 4
        ):
            cleaned.append(
                {
                    "question": item["question"],
                    "options": [str(option) for option in options],
                    "answer_index": int(item.get("answer_index", 0)),
                    "explanation": str(
                        item.get("explanation", "")
                    ),
                }
            )

    return cleaned


def generate_flashcards(doc_id: str, n: int = 10) -> list[dict]:
    _check_ollama()

    chunks = _get_document_chunks(doc_id)

    if not chunks:
        return []

    context = "\n\n".join(
        document for document, _ in chunks
    )[:30000]

    n = max(1, min(n, 30))

    prompt = f"""
Create {n} useful study flashcards from the following material.

Return ONLY valid JSON.
The JSON must be an array.
Each item must contain:
- front
- back

Keep the front as a question, term, or concept.
Keep the back as a clear explanation.

Study material:
{context}
"""

    raw = _generate(prompt)
    flashcards = _extract_json(raw)

    if not isinstance(flashcards, list):
        return []

    cleaned = []

    for item in flashcards[:n]:
        if not isinstance(item, dict):
            continue

        if "front" in item and "back" in item:
            cleaned.append(
                {
                    "front": str(item["front"]),
                    "back": str(item["back"]),
                }
            )

    return cleaned


def delete_document(doc_id: str) -> bool:
    registry = _load_registry()

    if doc_id not in registry:
        return False

    _collection.delete(where={"doc_id": doc_id})

    del registry[doc_id]
    _save_registry(registry)

    return True
