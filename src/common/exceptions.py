"""Custom exceptions for the cooking assistant application."""

class CookingAssistantError(Exception):
    """Base exception for all cooking assistant errors."""
    pass

class RecipeValidationError(CookingAssistantError):
    """Raised when recipe validation fails."""
    pass

class RecipeGenerationError(CookingAssistantError):
    """Raised when recipe generation fails."""
    pass

class ConfigurationError(CookingAssistantError):
    """Raised when configuration is invalid or missing."""
    pass

class TemplateError(CookingAssistantError):
    """Raised when template selection or creation fails."""
    pass

class SafetyValidationError(CookingAssistantError):
    """Raised when safety validation fails."""
    pass

class EmbeddingGenerationError(CookingAssistantError):
    """Raised when embedding generation fails."""
    pass

class VectorDatabaseError(CookingAssistantError):
    """Raised when vector database operations fail."""
    pass

class VectorSearchError(VectorDatabaseError):
    """Raised when vector search operations fail."""
    pass

class BM25IndexError(VectorDatabaseError):
    """Raised when BM25 index operations fail."""
    pass