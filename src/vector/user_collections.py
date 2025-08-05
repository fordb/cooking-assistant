"""
User recipe collections management for the vector database.
Provides functionality for user-specific recipe storage, validation, and retrieval.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from chromadb.errors import NotFoundError

from src.recipes.models import Recipe
from src.common.config import get_vector_config, get_logger
from src.common.exceptions import VectorDatabaseError, RecipeValidationError
from .types import UserRecipe, UserRecipeMetadata, SearchResult
from .store import VectorRecipeStore

logger = get_logger(__name__)


class UserRecipeCollectionError(VectorDatabaseError):
    """Exception raised for user recipe collection operations."""
    pass


class UserRecipeCollection:
    """
    Manages user-specific recipe collections in the vector database.
    Extends VectorRecipeStore functionality with user-specific operations.
    """
    
    def __init__(self, user_id: str, api_key: Optional[str] = None):
        """
        Initialize user recipe collection.
        
        Args:
            user_id: Unique identifier for the user
            api_key: OpenAI API key for embedding generation
            
        Raises:
            UserRecipeCollectionError: If user_id is invalid
        """
        self.config = get_vector_config()
        self.user_id = self._validate_user_id(user_id)
        self.collection_name = f"{self.config.USER_COLLECTION_PREFIX}{self.user_id}"
        
        # Initialize the underlying vector store with user's collection
        self.store = VectorRecipeStore(api_key=api_key, collection_name=self.collection_name)
        
        logger.info(f"Initialized user recipe collection for user: {self.user_id}")
    
    def _validate_user_id(self, user_id: str) -> str:
        """
        Validate user ID format and length.
        
        Args:
            user_id: User identifier to validate
            
        Returns:
            Validated user ID
            
        Raises:
            UserRecipeCollectionError: If user_id is invalid
        """
        if not user_id or not isinstance(user_id, str):
            raise UserRecipeCollectionError("User ID must be a non-empty string")
        
        if len(user_id) > self.config.USER_ID_MAX_LENGTH:
            raise UserRecipeCollectionError(f"User ID too long (max {self.config.USER_ID_MAX_LENGTH} chars)")
            
        # Check that user ID contains at least one alphanumeric character
        if not any(c.isalnum() for c in user_id):
            raise UserRecipeCollectionError("User ID must contain at least one alphanumeric character")
            
        # Sanitize user ID for collection name (replace invalid chars)
        sanitized = "".join(c if c.isalnum() or c in "-_" else "_" for c in user_id)
        
        return sanitized
    
    def add_user_recipe(self, recipe: Recipe) -> str:
        """
        Add a user-uploaded recipe to their collection.
        
        Args:
            recipe: Recipe object to add (already validated during instantiation)
            
        Returns:
            Recipe ID in the collection
            
        Raises:
            UserRecipeCollectionError: If storage fails or user exceeds recipe limit
        """
        try:
            # Recipe is already validated during instantiation (Pydantic models validate on creation)
            logger.debug(f"Adding recipe: {recipe.title}")
            
            # Check user recipe count limit
            current_count = self.get_user_recipe_count() 
            if current_count >= self.config.MAX_USER_RECIPES:
                raise UserRecipeCollectionError(
                    f"User recipe limit exceeded ({self.config.MAX_USER_RECIPES})"
                )
            
            # Create user recipe metadata
            timestamp = datetime.utcnow().isoformat()
            user_recipe_metadata = {
                "title": recipe.title,
                "difficulty": recipe.difficulty,
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time,
                "total_time": recipe.prep_time + recipe.cook_time,
                "servings": recipe.servings,
                "ingredient_count": len(recipe.ingredients),
                "instruction_count": len(recipe.instructions),
                "user_id": self.user_id,
                "uploaded_at": timestamp
            }
            
            # Store recipe in user's collection
            recipe_id = self.store.insert_recipe(recipe, metadata=user_recipe_metadata)
            logger.info(f"Added user recipe '{recipe.title}' with ID: {recipe_id}")
            
            return recipe_id
            
        except Exception as e:
            if isinstance(e, UserRecipeCollectionError):
                raise
            raise UserRecipeCollectionError(f"Failed to add user recipe: {str(e)}") from e
    
    def get_user_recipes(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all recipes from user's collection.
        
        Args:
            limit: Maximum number of recipes to return
            
        Returns:
            List of user recipes with metadata
        """
        try:
            search_limit = limit or self.config.DEFAULT_SEARCH_LIMIT
            
            # Get all recipes from user collection (using empty query gets all)
            results = self.store._collection.get(limit=search_limit)
            
            user_recipes = []
            for i, doc_id in enumerate(results['ids']):
                try:
                    metadata = results['metadatas'][i] if results['metadatas'] else {}
                    document = results['documents'][i] if results['documents'] else ""
                    
                    user_recipe = {
                        'id': doc_id,
                        'document': document,
                        'metadata': metadata,
                        'user_id': self.user_id
                    }
                    user_recipes.append(user_recipe)
                    
                except (IndexError, KeyError) as e:
                    logger.warning(f"Skipping malformed recipe result: {e}")
                    continue
            
            logger.info(f"Retrieved {len(user_recipes)} recipes for user: {self.user_id}")
            return user_recipes
            
        except Exception as e:
            raise UserRecipeCollectionError(f"Failed to retrieve user recipes: {str(e)}") from e
    
    def get_user_recipe_count(self) -> int:
        """
        Get the total number of recipes in user's collection.
        
        Returns:
            Number of recipes in collection
        """
        try:
            results = self.store._collection.count()
            logger.debug(f"User {self.user_id} has {results} recipes")
            return results
            
        except Exception as e:
            logger.warning(f"Failed to get recipe count for user {self.user_id}: {e}")
            return 0
    
    def search_user_recipes(self, query: str, n_results: Optional[int] = None, 
                           search_type: str = "hybrid") -> List[SearchResult]:
        """
        Search within user's recipe collection using various search methods.
        
        Args:
            query: Search query
            n_results: Maximum number of results to return
            search_type: Type of search ("dense", "sparse", "hybrid")
            
        Returns:
            List of search results from user's collection
        """
        try:
            # Use the underlying store's search methods
            if search_type == "dense":
                return self.store.search_recipes(query, n_results)
            elif search_type == "sparse":
                return self.store.search_recipes_sparse(query, n_results)
            elif search_type == "hybrid":
                return self.store.search_recipes_hybrid(query, n_results)
            else:
                raise UserRecipeCollectionError(f"Unknown search type: {search_type}")
                
        except Exception as e:
            raise UserRecipeCollectionError(f"Failed to search user recipes: {str(e)}") from e
    
    def delete_user_recipe(self, recipe_id: str) -> bool:
        """
        Delete a recipe from user's collection.
        
        Args:
            recipe_id: ID of recipe to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            UserRecipeCollectionError: If deletion fails
        """
        try:
            self.store._collection.delete(ids=[recipe_id])
            logger.info(f"Deleted recipe {recipe_id} for user: {self.user_id}")
            return True
            
        except Exception as e:
            raise UserRecipeCollectionError(f"Failed to delete recipe {recipe_id}: {str(e)}") from e
    
    def collection_exists(self) -> bool:
        """
        Check if user's collection exists in the database.
        
        Returns:
            True if collection exists
        """
        try:
            # Try to access the collection
            self.store._get_collection()
            return True
        except (NotFoundError, VectorDatabaseError):
            return False
    
    @property
    def stats(self) -> Dict[str, Any]:
        """
        Get statistics about user's recipe collection.
        
        Returns:
            Dictionary with collection statistics
        """
        return {
            'user_id': self.user_id,
            'collection_name': self.collection_name,
            'recipe_count': self.get_user_recipe_count(),
            'collection_exists': self.collection_exists(),
            'max_recipes': self.config.MAX_USER_RECIPES
        }