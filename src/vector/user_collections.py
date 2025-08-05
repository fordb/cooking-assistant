"""
User recipe collections management for the vector database.
Provides functionality for user-specific recipe storage, validation, and retrieval.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from chromadb.errors import NotFoundError

from src.recipes.models import Recipe
from src.common.config import get_vector_config, get_logger
from src.common.exceptions import VectorDatabaseError
from .types import UserRecipe, UserRecipeMetadata, SearchResult
from .store import VectorRecipeStore

logger = get_logger(__name__)


class UserRecipeCollectionError(VectorDatabaseError):
    """Exception raised for user recipe collection operations."""
    pass


class UserRecipeCollection:
    """Manages user-specific recipe collections in the vector database."""
    
    def __init__(self, user_id: str, api_key: Optional[str] = None):
        """Initialize user recipe collection.
        
        Args:
            user_id: Unique identifier for the user
            api_key: OpenAI API key for embedding generation
        """
        self.config = get_vector_config()
        self.user_id = self._validate_user_id(user_id)
        self.collection_name = f"{self.config.USER_COLLECTION_PREFIX}{self.user_id}"
        
        # Initialize the underlying vector store with user's collection
        self.store = VectorRecipeStore(api_key=api_key, collection_name=self.collection_name)
    
    def _validate_user_id(self, user_id: str) -> str:
        """Validate and sanitize user ID."""
        if not user_id or not isinstance(user_id, str):
            raise UserRecipeCollectionError("User ID must be a non-empty string")
        
        if len(user_id) > self.config.USER_ID_MAX_LENGTH:
            raise UserRecipeCollectionError(f"User ID too long (max {self.config.USER_ID_MAX_LENGTH} chars)")
            
        # Check that user ID contains at least one alphanumeric character
        if not any(c.isalnum() for c in user_id):
            raise UserRecipeCollectionError("User ID must contain at least one alphanumeric character")
            
        # Sanitize user ID for collection name (replace invalid chars)
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in user_id)
    
    def add_user_recipe(self, recipe: Recipe) -> str:
        """Add a user-uploaded recipe to their collection.
        
        Args:
            recipe: Recipe object to add
            
        Returns:
            Recipe ID in the collection
        """
        try:
            # Check user recipe count limit
            current_count = self.get_user_recipe_count() 
            if current_count >= self.config.MAX_USER_RECIPES:
                raise UserRecipeCollectionError(
                    f"User recipe limit exceeded ({self.config.MAX_USER_RECIPES})"
                )
            
            # Create user recipe metadata
            user_recipe_metadata = {
                "title": recipe.title,
                "difficulty": recipe.difficulty,
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time,
                "servings": recipe.servings,
                "user_id": self.user_id,
                "uploaded_at": datetime.utcnow().isoformat()
            }
            
            # Store recipe in user's collection
            return self.store.insert_recipe(recipe, metadata=user_recipe_metadata)
            
        except Exception as e:
            if isinstance(e, UserRecipeCollectionError):
                raise
            raise UserRecipeCollectionError(f"Failed to add user recipe: {str(e)}") from e
    
    def get_user_recipes(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve all recipes from user's collection."""
        try:
            search_limit = limit or self.config.DEFAULT_SEARCH_LIMIT
            
            # Get all recipes from user collection using the public collection property
            results = self.store.collection.get(limit=search_limit)
            
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
                    
                except (IndexError, KeyError):
                    continue
            
            return user_recipes
            
        except Exception as e:
            raise UserRecipeCollectionError(f"Failed to retrieve user recipes: {str(e)}") from e
    
    def get_user_recipe_count(self) -> int:
        """Get the total number of recipes in user's collection."""
        try:
            return self.store.count_recipes()
        except Exception:
            return 0
    
    def search_user_recipes(self, query: str, n_results: Optional[int] = None, 
                           search_type: str = "hybrid") -> List[SearchResult]:
        """Search within user's recipe collection."""
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
        """Delete a recipe from user's collection."""
        try:
            success = self.store.delete_recipe(recipe_id)
            if not success:
                raise UserRecipeCollectionError(f"Failed to delete recipe {recipe_id}")
            return True
        except Exception as e:
            raise UserRecipeCollectionError(f"Failed to delete recipe {recipe_id}: {str(e)}") from e
    
