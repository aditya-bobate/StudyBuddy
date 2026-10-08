"""Retrieval-augmented question answering over stored study documents."""

from __future__ import annotations

from .ingest import search_chunks
from .llm import chat

SYSTEM_PROMPT = """You are StudyBuddy, a careful study assistant.
Answer questions using ONLY the supplied document context.
If the context does not contain enough information, say that the answer is not available in the uploaded material.
Do not invent facts, sources, page numbers, or citations.
Keep the answer clear and useful for a student.
"""


def answer_question(
    question: str,
    doc_id: str | None = None,
    top_k: int = 4,
    history: list[dict] | None = None,
) -> dict:
    """Retrieve relevant chunks and generate a grounded answer with sources."""
    matches = search_chunks(question, doc_id=doc_id, top_k=top_k)
    if not matches:
        return {
            "answer": "I could not find relevant information in the uploaded material.",
            "sources": [],
        }

    context = "\n\n".join(
        f"[Source {i}] File: {item['file']} | Page: {item['page']}\n{item['text']}"
        for i, item in enumerate(matches, start=1)
    )
    history_text = ""
    if history:
        recent = history[-4:]
        history_text = "\n\nRecent conversation:\n" + "\n".join(
            f"{item.get('role', 'user').title()}: {item.get('content', '')}"
            for item in recent
            if item.get("content")
        )

    prompt = f"""Document context:\n{context}\n{history_text}\n\nQuestion: {question}\n\nAnswer from the document context only."""
    answer = chat(prompt, system=SYSTEM_PROMPT)
    sources = [
        {"file": item["file"], "page": item["page"], "snippet": item["text"][:400]}
        for item in matches
    ]
    return {"answer": answer, "sources": sources}
