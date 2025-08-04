"""Vector database operations for semantic recipe search and RAG."""

from .embeddings import RecipeEmbeddingGenerator, create_search_embedding
from .store import VectorRecipeStore, VectorStoreError
from .keywords import extract_recipe_keywords, extract_query_keywords, build_recipe_corpus
# from .ingestion import RecipeIngestionPipeline, run_example_ingestion  # Commented to avoid circular imports

__all__ = [
    'RecipeEmbeddingGenerator',
    'create_search_embedding',
    'VectorRecipeStore', 
    'VectorStoreError',
    'extract_recipe_keywords',
    'extract_query_keywords', 
    'build_recipe_corpus',
    # 'RecipeIngestionPipeline',
    # 'run_example_ingestion'
]