class StudyBuddyError(Exception):
    """Base exception for StudyBuddy."""

class OllamaNotRunning(StudyBuddyError):
    """Raised when the Ollama service is not reachable."""

class ModelMissing(StudyBuddyError):
    """Raised when a required Ollama model is not downloaded."""

class EmptyDocument(StudyBuddyError):
    """Raised when attempting to ingest an empty document."""

class UnsupportedFile(StudyBuddyError):
    """Raised when a file type is not supported for ingestion."""
