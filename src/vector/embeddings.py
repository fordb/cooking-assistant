"""
Recipe embedding generation using OpenAI's text-embedding-ada-002 model.
Handles text preparation and embedding creation for vector search.
"""

from openai import OpenAI
from typing import List, Dict, Optional, Union
import os
from src.recipes.models import Recipe
from src.common.config import get_vector_config, get_openai_config, get_logger
from src.common.exceptions import EmbeddingGenerationError

# Type definitions for better type safety
EmbeddingData = Dict[str, Union[str, List[float], Dict[str, Union[str, int, List[str]]]]]

logger = get_logger(__name__)

class RecipeEmbeddingGenerator:
    """Generates embeddings for recipes using OpenAI's embedding model."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the embedding generator.
        
        Args:
            api_key: OpenAI API key. If None, will use environment variable.
        """
        self.vector_config = get_vector_config()
        self.openai_config = get_openai_config()
        
        # Initialize OpenAI client with proper v1.x pattern
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            # This will automatically use OPENAI_API_KEY environment variable
            self.client = OpenAI()
        
        logger.info(f"Initialized RecipeEmbeddingGenerator with model: {self.vector_config.EMBEDDING_MODEL}")
    
    def prepare_recipe_text(self, recipe: Recipe) -> str:
        """
        Convert a recipe into optimized text for embedding generation.
        
        Args:
            recipe: Recipe object to convert
            
        Returns:
            Formatted text string optimized for semantic search
        """
        # Create comprehensive text that captures the recipe's essence
        components = [
            f"Recipe: {recipe.title}",
            f"Difficulty: {recipe.difficulty}",
            f"Cooking time: {recipe.prep_time} minutes prep, {recipe.cook_time} minutes cook",
            f"Serves {recipe.servings} people",
            f"Ingredients: {' | '.join(recipe.ingredients)}",
            f"Instructions: {' '.join(recipe.instructions)}"
        ]
        
        full_text = "\n".join(components)
        
        # Log text length for monitoring
        logger.debug(f"Prepared text for '{recipe.title}': {len(full_text)} characters")
        
        return full_text
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a text string using OpenAI API.
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
            
        Raises:
            EmbeddingGenerationError: If OpenAI API call fails
        """
        try:
            logger.debug(f"Generating embedding for text of length {len(text)}")
            
            response = self.client.embeddings.create(
                model=self.vector_config.EMBEDDING_MODEL,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            logger.debug(f"Generated embedding with dimension {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise EmbeddingGenerationError(f"OpenAI embedding generation failed: {e}") from e
    
    def generate_recipe_embedding(self, recipe: Recipe) -> EmbeddingData:
        """
        Generate embedding and metadata for a recipe.
        
        Args:
            recipe: Recipe to embed
            
        Returns:
            Dictionary with embedding, text, and metadata
        """
        logger.info(f"Generating embedding for recipe: {recipe.title}")
        
        # Prepare optimized text
        recipe_text = self.prepare_recipe_text(recipe)
        
        # Generate embedding
        embedding = self.generate_embedding(recipe_text)
        
        # Prepare metadata for vector database
        metadata = {
            "title": recipe.title,
            "difficulty": recipe.difficulty,
            "prep_time": recipe.prep_time,
            "cook_time": recipe.cook_time,
            "total_time": recipe.total_time,
            "servings": recipe.servings,
            "ingredient_count": len(recipe.ingredients),
            "instruction_count": len(recipe.instructions)
        }
        
        result = {
            "embedding": embedding,
            "text": recipe_text,
            "metadata": metadata,
            "recipe": recipe
        }
        
        logger.info(f"Successfully generated embedding for '{recipe.title}'")
        return result
    
    def generate_batch_embeddings(self, recipes: List[Recipe]) -> List[EmbeddingData]:
        """
        Generate embeddings for multiple recipes.
        
        Args:
            recipes: List of recipes to embed
            
        Returns:
            List of embedding dictionaries
        """
        logger.info(f"Generating embeddings for {len(recipes)} recipes")
        
        results = []
        for i, recipe in enumerate(recipes, 1):
            try:
                result = self.generate_recipe_embedding(recipe)
                results.append(result)
                logger.debug(f"Completed {i}/{len(recipes)}: {recipe.title}")
                
            except EmbeddingGenerationError as e:
                logger.error(f"Failed to generate embedding for '{recipe.title}': {e}")
                # Continue with other recipes instead of failing completely
                continue
        
        logger.info(f"Successfully generated {len(results)} embeddings out of {len(recipes)} recipes")
        return results

def create_search_embedding(query: str, api_key: Optional[str] = None) -> List[float]:
    """
    Generate embedding for a search query.
    
    Args:
        query: Search query text
        api_key: OpenAI API key
        
    Returns:
        Embedding vector for search
    """
    generator = RecipeEmbeddingGenerator(api_key)
    return generator.generate_embedding(query)

