"""Document extraction, chunking, embedding, and ChromaDB persistence."""

from __future__ import annotations

import hashlib
import logging
import os
import uuid
from pathlib import Path

import chromadb
from pypdf import PdfReader

from .errors import EmptyDocument, UnsupportedFile
from .llm import embed

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 20 * 1024 * 1024
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
SUPPORTED_EXTENSIONS = {".pdf", ".txt"}
CHROMA_PATH = os.getenv("STUDYBUDDY_CHROMA_PATH", ".chroma")
COLLECTION_NAME = "studybuddy_documents"

_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(name=COLLECTION_NAME)


def _extract_pdf(path: Path) -> list[tuple[str, int]]:
    """Extract non-empty text from a PDF, retaining its page number."""
    reader = PdfReader(str(path))
    pages: list[tuple[str, int]] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append((text, page_number))
    return pages


def _extract_text(path: Path) -> list[tuple[str, int]]:
    """Extract a UTF-8 text file as one logical page."""
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    return [(text, 1)] if text else []


def _chunk_words(text: str, page: int) -> list[tuple[str, int]]:
    """Split text into overlapping word-based chunks."""
    words = text.split()
    if not words:
        return []
    step = max(1, CHUNK_SIZE - CHUNK_OVERLAP)
    return [
        (" ".join(words[start : start + CHUNK_SIZE]), page)
        for start in range(0, len(words), step)
        if words[start : start + CHUNK_SIZE]
    ]


def _make_doc_id(path: Path) -> str:
    """Create a short unique identifier for an ingested document."""
    return f"{path.stem}-{uuid.uuid4().hex[:10]}"


def ingest_file(path: str) -> dict:
    """Extract, chunk, embed, and persist a PDF or TXT document."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not file_path.is_file():
        raise UnsupportedFile("The supplied path is not a file.")
    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFile("Only PDF and TXT files are supported.")
    if file_path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("File is larger than the 20 MB limit.")

    if file_path.suffix.lower() == ".pdf":
        pages = _extract_pdf(file_path)
    else:
        pages = _extract_text(file_path)

    chunks: list[tuple[str, int]] = []
    for page_text, page_number in pages:
        chunks.extend(_chunk_words(page_text, page_number))

    if not chunks:
        raise EmptyDocument(
            "Empty document: no extractable text was found. The PDF may be scanned/image-only. "
            "Use a text-based PDF or TXT file."
        )

    doc_id = _make_doc_id(file_path)
    texts = [text for text, _ in chunks]
    vectors = embed(texts)
    ids = [
        hashlib.sha1(f"{doc_id}:{i}".encode()).hexdigest() for i in range(len(texts))
    ]
    metadatas = [
        {"doc_id": doc_id, "file": file_path.name, "page": page} for _, page in chunks
    ]

    _collection.add(
        ids=ids,
        documents=texts,
        embeddings=vectors,
        metadatas=metadatas,
    )
    logger.info("Ingested %s as %s (%d chunks)", file_path.name, doc_id, len(chunks))
    return {"doc_id": doc_id, "name": file_path.name, "chunks": len(chunks)}


def list_documents() -> list[dict]:
    """Return unique documents currently stored in ChromaDB."""
    result = _collection.get(include=["metadatas"])
    documents: dict[str, str] = {}
    for metadata in result.get("metadatas") or []:
        if not metadata:
            continue
        doc_id = metadata.get("doc_id")
        name = metadata.get("file")
        if doc_id and name:
            documents[str(doc_id)] = str(name)
    return [{"doc_id": doc_id, "name": name} for doc_id, name in documents.items()]


def search_chunks(query: str, doc_id: str | None = None, top_k: int = 4) -> list[dict]:
    """Retrieve the most relevant stored chunks for a query."""
    if not query.strip():
        raise ValueError("Question cannot be empty.")
    if top_k < 1:
        return []

    query_embedding = embed(query)[0]
    kwargs: dict = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }
    if doc_id:
        kwargs["where"] = {"doc_id": doc_id}

    result = _collection.query(**kwargs)
    documents = result.get("documents") or [[]]
    metadatas = result.get("metadatas") or [[]]
    distances = result.get("distances") or [[]]

    matches: list[dict] = []
    for text, metadata, distance in zip(documents[0], metadatas[0], distances[0]):
        if not metadata:
            continue
        matches.append(
            {
                "text": text,
                "file": metadata.get("file", "unknown"),
                "page": int(metadata.get("page", 1)),
                "distance": float(distance),
            }
        )
    return matches


def get_document_chunks(doc_id: str) -> list[dict]:
    """Return all chunks for a document in their stored order."""
    result = _collection.get(
        where={"doc_id": doc_id},
        include=["documents", "metadatas"],
    )
    rows = []
    for text, metadata in zip(
        result.get("documents") or [], result.get("metadatas") or []
    ):
        if metadata:
            rows.append(
                {
                    "text": text,
                    "file": metadata.get("file", "unknown"),
                    "page": int(metadata.get("page", 1)),
                }
            )
    return rows


def delete_document(doc_id: str) -> bool:
    """Delete all stored chunks belonging to a document."""
    result = _collection.get(where={"doc_id": doc_id}, include=[])
    ids = result.get("ids") or []
    if not ids:
        return False
    _collection.delete(ids=ids)
    logger.info("Deleted document %s (%d chunks)", doc_id, len(ids))
    return True
