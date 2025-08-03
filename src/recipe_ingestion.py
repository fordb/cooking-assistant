"""
Recipe ingestion pipeline for loading recipes into vector database.
Handles batch processing and data migration from example recipes.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models import Recipe
from src.examples import load_example_recipes
from src.vector_store import VectorRecipeStore, VectorStoreError
from src.exceptions import EmbeddingGenerationError
from src.config import get_logger

logger = get_logger(__name__)

class RecipeIngestionPipeline:
    """Pipeline for ingesting recipes into the vector database."""
    
    def __init__(self, api_key: Optional[str] = None, collection_name: Optional[str] = None):
        """
        Initialize the ingestion pipeline.
        
        Args:
            api_key: OpenAI API key for embeddings
            collection_name: Target collection name
        """
        self.vector_store = VectorRecipeStore(api_key, collection_name)
        self.stats = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }
        
        logger.info("Initialized recipe ingestion pipeline")
    
    def ingest_example_recipes(self, clear_existing: bool = False) -> Dict[str, Any]:
        """
        Ingest recipes from data/example_recipes.json into vector database.
        
        Args:
            clear_existing: Whether to clear existing recipes first
            
        Returns:
            Dictionary with ingestion statistics
        """
        self.stats['start_time'] = datetime.now()
        logger.info("Starting ingestion of example recipes")
        
        try:
            # Clear existing recipes if requested
            if clear_existing:
                logger.info("Clearing existing recipes from collection")
                self.vector_store.clear_collection()
            
            # Load example recipes
            logger.info("Loading example recipes from data/example_recipes.json")
            recipes = load_example_recipes()
            logger.info(f"Loaded {len(recipes)} example recipes")
            
            # Generate recipe IDs based on titles (for consistency)
            recipe_ids = [self._generate_recipe_id(recipe) for recipe in recipes]
            
            # Ingest recipes
            result = self._ingest_recipes(recipes, recipe_ids)
            
            self.stats['end_time'] = datetime.now()
            self.stats['duration'] = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            
            logger.info(f"Ingestion completed: {self.stats['successful']}/{self.stats['processed']} recipes successful")
            return {
                'status': 'completed',
                'stats': self.stats,
                'recipe_ids': result
            }
            
        except Exception as e:
            self.stats['end_time'] = datetime.now()
            logger.error(f"Ingestion pipeline failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'stats': self.stats
            }
    
    def ingest_recipes(self, recipes: List[Recipe], recipe_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Ingest a list of recipes into the vector database.
        
        Args:
            recipes: List of Recipe objects to ingest
            recipe_ids: Optional list of custom IDs
            
        Returns:
            Dictionary with ingestion results
        """
        self.stats['start_time'] = datetime.now()
        logger.info(f"Starting ingestion of {len(recipes)} recipes")
        
        try:
            # Generate IDs if not provided
            if recipe_ids is None:
                recipe_ids = [self._generate_recipe_id(recipe) for recipe in recipes]
            
            # Ingest recipes
            result = self._ingest_recipes(recipes, recipe_ids)
            
            self.stats['end_time'] = datetime.now()
            self.stats['duration'] = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            
            return {
                'status': 'completed' if self.stats['successful'] > 0 else 'failed',
                'stats': self.stats,
                'recipe_ids': result
            }
            
        except Exception as e:
            self.stats['end_time'] = datetime.now()
            logger.error(f"Recipe ingestion failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'stats': self.stats
            }
    
    def _ingest_recipes(self, recipes: List[Recipe], recipe_ids: List[str]) -> List[str]:
        """
        Internal method to handle recipe ingestion.
        
        Args:
            recipes: List of recipes to ingest
            recipe_ids: List of recipe IDs
            
        Returns:
            List of successfully ingested recipe IDs
        """
        self.stats['processed'] = len(recipes)
        successful_ids = []
        
        try:
            # Use batch ingestion for efficiency
            logger.info("Starting batch ingestion...")
            ingested_ids = self.vector_store.add_recipes(recipes, recipe_ids)
            successful_ids.extend(ingested_ids)
            self.stats['successful'] = len(ingested_ids)
            self.stats['failed'] = len(recipes) - len(ingested_ids)
            
            logger.info(f"Batch ingestion completed: {len(ingested_ids)} recipes added")
            
        except VectorStoreError as e:
            logger.warning(f"Batch ingestion failed, falling back to individual ingestion: {e}")
            
            # Fall back to individual ingestion
            for i, (recipe, recipe_id) in enumerate(zip(recipes, recipe_ids)):
                try:
                    ingested_id = self.vector_store.add_recipe(recipe, recipe_id)
                    successful_ids.append(ingested_id)
                    self.stats['successful'] += 1
                    logger.debug(f"Successfully ingested recipe {i+1}/{len(recipes)}: {recipe.title}")
                    
                except (VectorStoreError, EmbeddingGenerationError) as recipe_error:
                    self.stats['failed'] += 1
                    logger.error(f"Failed to ingest recipe '{recipe.title}': {recipe_error}")
                    continue
        
        return successful_ids
    
    def _generate_recipe_id(self, recipe: Recipe) -> str:
        """
        Generate a consistent ID for a recipe based on its title.
        
        Args:
            recipe: Recipe object
            
        Returns:
            Generated recipe ID
        """
        # Create ID from title (lowercase, replace spaces with underscores, remove special chars)
        title_id = recipe.title.lower().replace(' ', '_').replace('-', '_')
        # Keep only alphanumeric characters and underscores
        clean_id = ''.join(c for c in title_id if c.isalnum() or c == '_')
        return f"recipe_{clean_id}"
    
    def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get current ingestion statistics."""
        return self.stats.copy()
    
    def verify_ingestion(self) -> Dict[str, Any]:
        """
        Verify the ingestion by checking recipes in the database.
        
        Returns:
            Verification results
        """
        logger.info("Verifying recipe ingestion")
        
        try:
            # Count recipes in database
            recipe_count = self.vector_store.count_recipes()
            
            # Try a test search
            test_results = self.vector_store.search_recipes("chicken", n_results=3)
            
            verification = {
                'total_recipes': recipe_count,
                'test_search_results': len(test_results),
                'status': 'success' if recipe_count > 0 else 'warning'
            }
            
            logger.info(f"Verification complete: {recipe_count} recipes in database")
            return verification
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

def run_example_ingestion(api_key: Optional[str] = None, clear_existing: bool = True) -> Dict[str, Any]:
    """
    Convenience function to run example recipe ingestion.
    
    Args:
        api_key: OpenAI API key
        clear_existing: Whether to clear existing recipes
        
    Returns:
        Ingestion results
    """
    pipeline = RecipeIngestionPipeline(api_key)
    result = pipeline.ingest_example_recipes(clear_existing)
    
    # Add verification
    if result['status'] == 'completed':
        verification = pipeline.verify_ingestion()
        result['verification'] = verification
    
    return result