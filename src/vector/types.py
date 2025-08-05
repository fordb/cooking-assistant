"""
Type definitions for vector database operations.
Centralized location for all vector-related type definitions.
"""

from typing import List, Dict, Optional, Union, TypedDict
from src.recipes.models import Recipe

# Recipe metadata structure
RecipeMetadata = Dict[str, Union[str, int, List[str]]]

# Search result structure
SearchResult = Dict[str, Union[str, float, RecipeMetadata]]

# Filter dictionary structure
FilterDict = Dict[str, Optional[Union[str, List[str]]]]

# Ingestion statistics structure
IngestionStats = Dict[str, Union[str, int, List[str], bool]]

# Embedding-specific types
class EmbeddingMetadata(TypedDict):
    """Metadata structure for recipe embeddings."""
    title: str
    difficulty: str
    prep_time: int
    cook_time: int
    total_time: int
    servings: int
    ingredient_count: int
    instruction_count: int

class EmbeddingData(TypedDict):
    """Structure for recipe embedding data."""
    embedding: List[float]
    text: str
    metadata: EmbeddingMetadata
    recipe: Recipe