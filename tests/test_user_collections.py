"""
Tests for user recipe collections functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.vector.user_collections import UserRecipeCollection, UserRecipeCollectionError
from src.recipes.models import Recipe
from src.common.exceptions import RecipeValidationError


class TestUserRecipeCollection(unittest.TestCase):
    """Test user recipe collection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_user_id = "test_user_123"
        self.invalid_user_ids = ["", None, "a" * 150, "@#$%^&*"]
        
        # Create test recipe
        self.test_recipe = Recipe(
            title="Test Recipe",
            ingredients=["ingredient1", "ingredient2"],
            instructions=["step1", "step2", "step3"],
            prep_time=15,
            cook_time=30,
            servings=4,
            difficulty="Intermediate"
        )
        
        # Mock vector config
        self.mock_config = Mock()
        self.mock_config.USER_COLLECTION_PREFIX = "user_recipes_"
        self.mock_config.USER_ID_MAX_LENGTH = 100
        self.mock_config.MAX_USER_RECIPES = 1000
        self.mock_config.DEFAULT_SEARCH_LIMIT = 10
    
    @patch('src.vector.user_collections.get_vector_config')
    @patch('src.vector.user_collections.VectorRecipeStore')
    def test_user_collection_initialization(self, mock_store, mock_config):
        """Test user collection initialization."""
        mock_config.return_value = self.mock_config
        
        collection = UserRecipeCollection(self.test_user_id)
        
        self.assertEqual(collection.user_id, self.test_user_id)
        self.assertEqual(collection.collection_name, f"user_recipes_{self.test_user_id}")
        mock_store.assert_called_once()
    
    @patch('src.vector.user_collections.get_vector_config')
    def test_user_id_validation_valid(self, mock_config):
        """Test valid user ID acceptance."""
        mock_config.return_value = self.mock_config
        
        valid_ids = ["user123", "test-user", "user_name", "123", "a1b2c3"]
        
        for user_id in valid_ids:
            with patch('src.vector.user_collections.VectorRecipeStore'):
                collection = UserRecipeCollection(user_id)
                self.assertIsInstance(collection.user_id, str)
                self.assertGreater(len(collection.user_id), 0)
    
    @patch('src.vector.user_collections.get_vector_config')
    def test_user_id_validation_invalid(self, mock_config):
        """Test invalid user ID rejection."""
        mock_config.return_value = self.mock_config
        
        for invalid_id in self.invalid_user_ids:
            with self.assertRaises(UserRecipeCollectionError):
                with patch('src.vector.user_collections.VectorRecipeStore'):
                    UserRecipeCollection(invalid_id)
    
    @patch('src.vector.user_collections.get_vector_config')
    @patch('src.vector.user_collections.VectorRecipeStore')
    def test_user_id_sanitization(self, mock_store, mock_config):
        """Test user ID sanitization for collection names."""
        mock_config.return_value = self.mock_config
        
        # Test that special characters get replaced with underscores
        collection = UserRecipeCollection("user@example.com")
        self.assertEqual(collection.user_id, "user_example_com")
    
    @patch('src.vector.user_collections.get_vector_config')
    @patch('src.vector.user_collections.VectorRecipeStore')
    def test_add_user_recipe_success(self, mock_store, mock_config):
        """Test successful recipe addition."""
        mock_config.return_value = self.mock_config
        mock_store_instance = Mock()
        mock_store.return_value = mock_store_instance
        mock_store_instance.insert_recipe.return_value = "recipe_123"
        
        collection = UserRecipeCollection(self.test_user_id)
        collection.get_user_recipe_count = Mock(return_value=0)
        
        recipe_id = collection.add_user_recipe(self.test_recipe)
        
        self.assertEqual(recipe_id, "recipe_123")
        mock_store_instance.insert_recipe.assert_called_once()
        
        # Check that metadata includes user_id and timestamp
        call_args = mock_store_instance.insert_recipe.call_args
        metadata = call_args[1]['metadata']
        self.assertEqual(metadata['user_id'], self.test_user_id)
        self.assertIn('uploaded_at', metadata)
    
    @patch('src.vector.user_collections.get_vector_config')
    @patch('src.vector.user_collections.VectorRecipeStore')
    def test_add_user_recipe_validation_error(self, mock_store, mock_config):
        """Test recipe addition with validation error."""
        mock_config.return_value = self.mock_config
        
        collection = UserRecipeCollection(self.test_user_id)
        
        # Create invalid recipe that will fail validation during creation
        with self.assertRaises(RecipeValidationError):
            Recipe(
                title="",  # Empty title should fail validation
                ingredients=[],  # Empty ingredients should fail validation
                instructions=[],  # Empty instructions should fail validation
                prep_time=15,
                cook_time=30,
                servings=4,
                difficulty="Intermediate"
            )
    
    @patch('src.vector.user_collections.get_vector_config')
    @patch('src.vector.user_collections.VectorRecipeStore')
    def test_add_user_recipe_limit_exceeded(self, mock_store, mock_config):
        """Test recipe addition when user limit is exceeded."""
        mock_config.return_value = self.mock_config
        
        collection = UserRecipeCollection(self.test_user_id)
        collection.get_user_recipe_count = Mock(return_value=1000)  # At limit
        
        with self.assertRaises(UserRecipeCollectionError) as context:
            collection.add_user_recipe(self.test_recipe)
            
        self.assertIn("recipe limit exceeded", str(context.exception).lower())
    
    @patch('src.vector.user_collections.get_vector_config')
    @patch('src.vector.user_collections.VectorRecipeStore')
    def test_get_user_recipes(self, mock_store, mock_config):
        """Test retrieval of user recipes."""
        mock_config.return_value = self.mock_config
        mock_store_instance = Mock()
        mock_store.return_value = mock_store_instance
        
        # Mock collection results
        mock_collection = Mock()
        mock_store_instance.collection = mock_collection
        mock_collection.get.return_value = {
            'ids': ['recipe1', 'recipe2'],
            'documents': ['Recipe 1 content', 'Recipe 2 content'],
            'metadatas': [
                {'title': 'Recipe 1', 'user_id': self.test_user_id},
                {'title': 'Recipe 2', 'user_id': self.test_user_id}
            ]
        }
        
        collection = UserRecipeCollection(self.test_user_id)
        recipes = collection.get_user_recipes()
        
        self.assertEqual(len(recipes), 2)
        self.assertEqual(recipes[0]['id'], 'recipe1')
        self.assertEqual(recipes[0]['user_id'], self.test_user_id)
        self.assertEqual(recipes[1]['id'], 'recipe2')
    
    @patch('src.vector.user_collections.get_vector_config')
    @patch('src.vector.user_collections.VectorRecipeStore')
    def test_get_user_recipe_count(self, mock_store, mock_config):
        """Test getting user recipe count."""
        mock_config.return_value = self.mock_config
        mock_store_instance = Mock()
        mock_store.return_value = mock_store_instance
        
        mock_store_instance.count_recipes.return_value = 5
        
        collection = UserRecipeCollection(self.test_user_id)
        count = collection.get_user_recipe_count()
        
        self.assertEqual(count, 5)
    
    @patch('src.vector.user_collections.get_vector_config')
    @patch('src.vector.user_collections.VectorRecipeStore')
    def test_search_user_recipes_hybrid(self, mock_store, mock_config):
        """Test searching user recipes with hybrid search."""
        mock_config.return_value = self.mock_config
        mock_store_instance = Mock()
        mock_store.return_value = mock_store_instance
        
        expected_results = [{'id': 'recipe1', 'similarity': 0.8}]
        mock_store_instance.search_recipes_hybrid.return_value = expected_results
        
        collection = UserRecipeCollection(self.test_user_id)
        results = collection.search_user_recipes("chicken", search_type="hybrid")
        
        self.assertEqual(results, expected_results)
        mock_store_instance.search_recipes_hybrid.assert_called_once_with("chicken", None)
    
    @patch('src.vector.user_collections.get_vector_config')
    @patch('src.vector.user_collections.VectorRecipeStore')
    def test_search_user_recipes_dense(self, mock_store, mock_config):
        """Test searching user recipes with dense search."""
        mock_config.return_value = self.mock_config
        mock_store_instance = Mock()
        mock_store.return_value = mock_store_instance
        
        collection = UserRecipeCollection(self.test_user_id)
        collection.search_user_recipes("pasta", search_type="dense")
        
        mock_store_instance.search_recipes.assert_called_once_with("pasta", None)
    
    @patch('src.vector.user_collections.get_vector_config')
    @patch('src.vector.user_collections.VectorRecipeStore')
    def test_search_user_recipes_sparse(self, mock_store, mock_config):
        """Test searching user recipes with sparse search."""
        mock_config.return_value = self.mock_config
        mock_store_instance = Mock()
        mock_store.return_value = mock_store_instance
        
        collection = UserRecipeCollection(self.test_user_id)
        collection.search_user_recipes("soup", search_type="sparse")
        
        mock_store_instance.search_recipes_sparse.assert_called_once_with("soup", None)
    
    @patch('src.vector.user_collections.get_vector_config')
    @patch('src.vector.user_collections.VectorRecipeStore')
    def test_search_user_recipes_invalid_type(self, mock_store, mock_config):
        """Test searching with invalid search type."""
        mock_config.return_value = self.mock_config
        
        collection = UserRecipeCollection(self.test_user_id)
        
        with self.assertRaises(UserRecipeCollectionError) as context:
            collection.search_user_recipes("query", search_type="invalid")
            
        self.assertIn("Unknown search type", str(context.exception))
    
    @patch('src.vector.user_collections.get_vector_config')
    @patch('src.vector.user_collections.VectorRecipeStore')
    def test_delete_user_recipe(self, mock_store, mock_config):
        """Test deleting user recipe."""
        mock_config.return_value = self.mock_config
        mock_store_instance = Mock()
        mock_store.return_value = mock_store_instance
        
        mock_store_instance.delete_recipe.return_value = True
        
        collection = UserRecipeCollection(self.test_user_id)
        result = collection.delete_user_recipe("recipe_123")
        
        self.assertTrue(result)
        mock_store_instance.delete_recipe.assert_called_once_with("recipe_123")
    
    @patch('src.vector.user_collections.get_vector_config')
    @patch('src.vector.user_collections.VectorRecipeStore')
    def test_collection_exists_true(self, mock_store, mock_config):
        """Test collection exists check when collection exists."""
        mock_config.return_value = self.mock_config
        mock_store_instance = Mock()
        mock_store.return_value = mock_store_instance
        mock_store_instance.collection = Mock()
        
        collection = UserRecipeCollection(self.test_user_id)
        exists = collection.collection_exists()
        
        self.assertTrue(exists)
    
    @patch('src.vector.user_collections.get_vector_config')
    @patch('src.vector.user_collections.VectorRecipeStore')
    def test_collection_exists_false(self, mock_store, mock_config):
        """Test collection exists check when collection doesn't exist."""
        mock_config.return_value = self.mock_config
        mock_store_instance = Mock()
        mock_store.return_value = mock_store_instance
        
        from chromadb.errors import NotFoundError
        
        # Create a mock that raises NotFoundError when .collection is accessed
        def collection_property():
            raise NotFoundError("Not found")
        
        type(mock_store_instance).collection = property(lambda self: collection_property())
        
        collection = UserRecipeCollection(self.test_user_id)
        exists = collection.collection_exists()
        
        self.assertFalse(exists)
    
    @patch('src.vector.user_collections.get_vector_config')
    @patch('src.vector.user_collections.VectorRecipeStore')
    def test_stats_property(self, mock_store, mock_config):
        """Test collection stats property."""
        mock_config.return_value = self.mock_config
        
        collection = UserRecipeCollection(self.test_user_id)
        collection.get_user_recipe_count = Mock(return_value=3)
        collection.collection_exists = Mock(return_value=True)
        
        stats = collection.stats
        
        expected_stats = {
            'user_id': self.test_user_id,
            'collection_name': f"user_recipes_{self.test_user_id}",
            'recipe_count': 3,
            'collection_exists': True,
            'max_recipes': 1000
        }
        
        self.assertEqual(stats, expected_stats)


if __name__ == '__main__':
    unittest.main()