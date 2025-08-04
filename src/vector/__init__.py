"""Vector database operations for semantic recipe search and RAG."""

from .embeddings import RecipeEmbeddingGenerator, create_search_embedding
from .store import VectorRecipeStore, VectorStoreError
# from .ingestion import RecipeIngestionPipeline, run_example_ingestion  # Commented to avoid circular imports

__all__ = [
    'RecipeEmbeddingGenerator',
    'create_search_embedding',
    'VectorRecipeStore', 
    'VectorStoreError',
    # 'RecipeIngestionPipeline',
    # 'run_example_ingestion'
]