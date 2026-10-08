"""Small, reliable wrapper around the local Ollama service."""

from __future__ import annotations

import os
from collections.abc import Sequence

import ollama
from dotenv import load_dotenv

from .errors import ModelMissing, OllamaNotRunning

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

_client = ollama.Client(host=OLLAMA_HOST)


def _is_connection_error(exc: Exception) -> bool:
    """Return True when an Ollama exception represents an unreachable server."""
    message = str(exc).lower()
    return any(
        phrase in message
        for phrase in (
            "connection refused",
            "failed to connect",
            "connection reset",
            "connection error",
            "cannot connect",
            "max retries exceeded",
        )
    )


def _ensure_model(model: str) -> None:
    """Check that a requested model exists on the local Ollama server."""
    try:
        _client.show(model)
    except ollama.ResponseError as exc:
        if getattr(exc, "status_code", None) == 404 or "not found" in str(exc).lower():
            raise ModelMissing(
                f"Ollama model '{model}' is not installed. Run: ollama pull {model}"
            ) from exc
        if _is_connection_error(exc):
            raise OllamaNotRunning(
                f"Ollama is not reachable at {OLLAMA_HOST}. Start Ollama and try again."
            ) from exc
        raise
    except Exception as exc:
        if _is_connection_error(exc):
            raise OllamaNotRunning(
                f"Ollama is not reachable at {OLLAMA_HOST}. Start Ollama and try again."
            ) from exc
        raise


def chat(prompt: str, system: str | None = None) -> str:
    """Generate a response with the configured local chat model."""
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    _ensure_model(OLLAMA_MODEL)
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = _client.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            options={"temperature": 0.2},
        )
        content = getattr(getattr(response, "message", None), "content", None)
        if content is None and isinstance(response, dict):
            content = response.get("message", {}).get("content")
        if not content:
            raise RuntimeError("Ollama returned an empty response.")
        return str(content).strip()
    except ollama.ResponseError as exc:
        if getattr(exc, "status_code", None) == 404 or "not found" in str(exc).lower():
            raise ModelMissing(
                f"Ollama model '{OLLAMA_MODEL}' is not installed. Run: ollama pull {OLLAMA_MODEL}"
            ) from exc
        if _is_connection_error(exc):
            raise OllamaNotRunning(
                f"Ollama is not reachable at {OLLAMA_HOST}. Start Ollama and try again."
            ) from exc
        raise
    except Exception as exc:
        if _is_connection_error(exc):
            raise OllamaNotRunning(
                f"Ollama is not reachable at {OLLAMA_HOST}. Start Ollama and try again."
            ) from exc
        raise


def embed(texts: str | Sequence[str]) -> list[list[float]]:
    """Create embeddings for one or more pieces of text using Ollama."""
    values = [texts] if isinstance(texts, str) else list(texts)
    if not values:
        return []
    if any(not value.strip() for value in values):
        raise ValueError("Cannot embed empty text.")

    _ensure_model(EMBEDDING_MODEL)
    try:
        response = _client.embed(model=EMBEDDING_MODEL, input=values)
        embeddings = getattr(response, "embeddings", None)
        if embeddings is None and isinstance(response, dict):
            embeddings = response.get("embeddings")
        if not embeddings:
            raise RuntimeError("Ollama returned no embeddings.")
        return [list(map(float, vector)) for vector in embeddings]
    except ollama.ResponseError as exc:
        if getattr(exc, "status_code", None) == 404 or "not found" in str(exc).lower():
            raise ModelMissing(
                f"Ollama embedding model '{EMBEDDING_MODEL}' is not installed. "
                f"Run: ollama pull {EMBEDDING_MODEL}"
            ) from exc
        if _is_connection_error(exc):
            raise OllamaNotRunning(
                f"Ollama is not reachable at {OLLAMA_HOST}. Start Ollama and try again."
            ) from exc
        raise
    except Exception as exc:
        if _is_connection_error(exc):
            raise OllamaNotRunning(
                f"Ollama is not reachable at {OLLAMA_HOST}. Start Ollama and try again."
            ) from exc
        raise
