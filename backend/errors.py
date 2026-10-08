class StudyBuddyError(Exception):
    """Base exception for StudyBuddy."""
    pass

class OllamaNotRunning(StudyBuddyError):
    """Raised when the Ollama service is not reachable."""
    pass

class ModelMissing(StudyBuddyError):
    """Raised when a required Ollama model is not downloaded."""
    pass

class EmptyDocument(StudyBuddyError):
    """Raised when attempting to ingest an empty document."""
    pass

class UnsupportedFile(StudyBuddyError):
    """Raised when a file type is not supported for ingestion."""
    pass
