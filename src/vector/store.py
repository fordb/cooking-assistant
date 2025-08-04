"""
Vector database operations for recipe storage and retrieval.
Provides a high-level interface to Chroma DB operations.
"""

import chromadb
from typing import List, Dict, Any, Optional, Tuple
import uuid
from datetime import datetime

from src.recipes.models import Recipe
from src.common.config import get_vector_config, get_logger
from .embeddings import RecipeEmbeddingGenerator, create_search_embedding
from src.common.exceptions import CookingAssistantError

logger = get_logger(__name__)

class VectorStoreError(CookingAssistantError):
    """Exception raised for vector store operations."""
    pass

class VectorRecipeStore:
    """
    High-level interface for storing and searching recipes in vector database.
    Handles Chroma DB operations with recipe-specific logic.
    """
    
    def __init__(self, api_key: Optional[str] = None, collection_name: Optional[str] = None):
        """
        Initialize the vector recipe store.
        
        Args:
            api_key: OpenAI API key for embedding generation
            collection_name: Name of the collection to use (defaults to config)
        """
        self.config = get_vector_config()
        self.api_key = api_key
        self.collection_name = collection_name or self.config.RECIPE_COLLECTION_NAME
        
        # Initialize embedding generator
        self.embedding_generator = RecipeEmbeddingGenerator(api_key)
        
        # Initialize Chroma client
        self._client = None
        self._collection = None
        
        logger.info(f"Initialized VectorRecipeStore with collection: {self.collection_name}")
    
    @property
    def client(self):
        """Lazy initialization of Chroma client."""
        if self._client is None:
            try:
                self._client = chromadb.HttpClient(
                    host=self.config.HOST, 
                    port=self.config.PORT
                )
                # Test connection
                self._client.heartbeat()
                logger.debug("Connected to Chroma DB")
            except Exception as e:
                raise VectorStoreError(f"Failed to connect to Chroma DB at {self.config.HOST}:{self.config.PORT}: {e}")
        return self._client
    
    @property 
    def collection(self):
        """Lazy initialization of collection."""
        if self._collection is None:
            try:
                # Try to get existing collection
                self._collection = self.client.get_collection(self.collection_name)
                logger.debug(f"Connected to existing collection: {self.collection_name}")
            except ValueError:
                # Create new collection if it doesn't exist (Chroma raises ValueError for missing collections)
                self._collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={
                        "description": "Recipe collection for semantic search",
                        "created_at": datetime.now().isoformat()
                    }
                )
                logger.info(f"Created new collection: {self.collection_name}")
        return self._collection
    
    def add_recipe(self, recipe: Recipe, recipe_id: Optional[str] = None) -> str:
        """
        Add a single recipe to the vector store.
        
        Args:
            recipe: Recipe object to add
            recipe_id: Optional custom ID (generates UUID if not provided)
            
        Returns:
            ID of the added recipe
        """
        if recipe_id is None:
            recipe_id = f"recipe_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Adding recipe '{recipe.title}' with ID: {recipe_id}")
        
        try:
            # Generate embedding
            embedding_data = self.embedding_generator.generate_recipe_embedding(recipe)
            
            # Add to collection
            self.collection.add(
                embeddings=[embedding_data["embedding"]],
                documents=[embedding_data["text"]],
                metadatas=[embedding_data["metadata"]],
                ids=[recipe_id]
            )
            
            logger.info(f"Successfully added recipe '{recipe.title}' to vector store")
            return recipe_id
            
        except Exception as e:
            raise VectorStoreError(f"Failed to add recipe '{recipe.title}': {e}")
    
    def add_recipes(self, recipes: List[Recipe], recipe_ids: Optional[List[str]] = None) -> List[str]:
        """
        Add multiple recipes to the vector store.
        
        Args:
            recipes: List of Recipe objects to add
            recipe_ids: Optional list of custom IDs
            
        Returns:
            List of IDs for added recipes
        """
        if recipe_ids is None:
            recipe_ids = [f"recipe_{uuid.uuid4().hex[:8]}" for _ in recipes]
        
        if len(recipe_ids) != len(recipes):
            raise VectorStoreError("Number of recipe IDs must match number of recipes")
        
        logger.info(f"Adding {len(recipes)} recipes to vector store")
        
        try:
            # Generate embeddings for all recipes
            embedding_results = self.embedding_generator.generate_batch_embeddings(recipes)
            
            if not embedding_results:
                raise VectorStoreError("No embeddings were generated")
            
            # Prepare data for batch insert
            embeddings = [result["embedding"] for result in embedding_results]
            documents = [result["text"] for result in embedding_results]
            metadatas = [result["metadata"] for result in embedding_results]
            
            # Use only the IDs for recipes that were successfully embedded
            used_ids = recipe_ids[:len(embedding_results)]
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=used_ids
            )
            
            logger.info(f"Successfully added {len(embedding_results)} recipes to vector store")
            return used_ids
            
        except Exception as e:
            raise VectorStoreError(f"Failed to add recipes: {e}")
    
    def search_recipes(self, query: str, n_results: Optional[int] = None, 
                      min_similarity: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Search for recipes using semantic similarity.
        
        Args:
            query: Search query text
            n_results: Maximum number of results (defaults to config)
            min_similarity: Minimum similarity threshold (0-1)
            
        Returns:
            List of search results with metadata and similarity scores
        """
        n_results = n_results or self.config.DEFAULT_SEARCH_LIMIT
        min_similarity = min_similarity or (1 - self.config.SIMILARITY_THRESHOLD)
        
        logger.info(f"Searching recipes for: '{query}' (limit: {n_results})")
        
        try:
            # Generate embedding for search query
            query_embedding = create_search_embedding(query, self.api_key)
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Process results
            search_results = []
            for i in range(len(results['ids'][0])):
                distance = results['distances'][0][i]
                similarity = 1 - distance
                
                # Filter by minimum similarity
                if similarity < min_similarity:
                    continue
                
                result = {
                    'id': results['ids'][0][i],
                    'similarity': similarity,
                    'metadata': results['metadatas'][0][i],
                    'document': results['documents'][0][i]
                }
                search_results.append(result)
            
            logger.info(f"Found {len(search_results)} recipes matching '{query}'")
            return search_results
            
        except Exception as e:
            raise VectorStoreError(f"Failed to search recipes: {e}")
    
    def get_recipe_by_id(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a recipe by its ID.
        
        Args:
            recipe_id: ID of the recipe to retrieve
            
        Returns:
            Recipe data or None if not found
        """
        try:
            results = self.collection.get(ids=[recipe_id])
            
            if not results['ids']:
                return None
            
            return {
                'id': results['ids'][0],
                'metadata': results['metadatas'][0],
                'document': results['documents'][0]
            }
            
        except Exception as e:
            logger.error(f"Failed to get recipe {recipe_id}: {e}")
            return None
    
    def update_recipe(self, recipe_id: str, recipe: Recipe) -> bool:
        """
        Update an existing recipe in the vector store.
        
        Args:
            recipe_id: ID of recipe to update
            recipe: New recipe data
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Updating recipe {recipe_id}: {recipe.title}")
        
        try:
            # Generate new embedding
            embedding_data = self.embedding_generator.generate_recipe_embedding(recipe)
            
            # Update in collection
            self.collection.update(
                ids=[recipe_id],
                embeddings=[embedding_data["embedding"]],
                documents=[embedding_data["text"]],
                metadatas=[embedding_data["metadata"]]
            )
            
            logger.info(f"Successfully updated recipe {recipe_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update recipe {recipe_id}: {e}")
            return False
    
    def delete_recipe(self, recipe_id: str) -> bool:
        """
        Delete a recipe from the vector store.
        
        Args:
            recipe_id: ID of recipe to delete
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Deleting recipe {recipe_id}")
        
        try:
            self.collection.delete(ids=[recipe_id])
            logger.info(f"Successfully deleted recipe {recipe_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete recipe {recipe_id}: {e}")
            return False
    
    def count_recipes(self) -> int:
        """Get total number of recipes in the store."""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Failed to count recipes: {e}")
            return 0
    
    
    def clear_collection(self) -> bool:
        """
        Clear all recipes from the collection.
        
        Returns:
            True if successful
        """
        logger.warning("Clearing all recipes from collection")
        
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(self.collection_name)
            self._collection = None  # Reset cached collection
            
            # Recreate collection (will happen on next access)
            _ = self.collection
            
            logger.info("Successfully cleared collection")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False