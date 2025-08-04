"""Common utilities and shared functionality."""

from .config import get_config, get_logger
from .exceptions import CookingAssistantError, EmbeddingGenerationError
from .utils import *

__all__ = [
    'get_config',
    'get_logger',
    'CookingAssistantError',
    'EmbeddingGenerationError'
]