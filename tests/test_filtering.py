"""
Tests for recipe filtering functionality.
"""

import unittest
from unittest.mock import Mock, patch

from src.vector.filters import RecipeFilter, apply_metadata_filters, FilterValidationError
from src.vector.store import VectorRecipeStore


class TestRecipeFilter(unittest.TestCase):
    """Test RecipeFilter validation."""
    
    def test_valid_filter_creation(self):
        """Test creating valid filters."""
        filter1 = RecipeFilter(difficulty="Beginner")
        self.assertEqual(filter1.difficulty, "Beginner")
        
        filter2 = RecipeFilter(prep_time_min=10, prep_time_max=30, servings_max=4)
        self.assertEqual(filter2.prep_time_min, 10)
        self.assertTrue(filter2.has_filters())
        
        empty_filter = RecipeFilter()
        self.assertFalse(empty_filter.has_filters())
    
    def test_invalid_filters(self):
        """Test validation catches invalid filters."""
        with self.assertRaises(FilterValidationError):
            RecipeFilter(difficulty="Expert")  # Invalid difficulty
        
        with self.assertRaises(FilterValidationError):
            RecipeFilter(prep_time_min=60, prep_time_max=30)  # Min > max
        
        with self.assertRaises(FilterValidationError):
            RecipeFilter(dietary_restrictions=["invalid-diet"])


class TestApplyMetadataFilters(unittest.TestCase):
    """Test applying filters to search results."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_results = [
            {
                'id': 'recipe1',
                'metadata': {
                    'title': 'Chicken Stir Fry',
                    'difficulty': 'Beginner',
                    'prep_time': 15,
                    'cook_time': 10,
                    'servings': 4
                }
            },
            {
                'id': 'recipe2', 
                'metadata': {
                    'title': 'Advanced Roast',
                    'difficulty': 'Advanced',
                    'prep_time': 30,
                    'cook_time': 120,
                    'servings': 8
                }
            }
        ]
    
    def test_no_filters(self):
        """Test that no filters returns all results."""
        result = apply_metadata_filters(self.sample_results, RecipeFilter())
        self.assertEqual(len(result), 2)
    
    def test_difficulty_filter(self):
        """Test difficulty filtering."""
        filter_obj = RecipeFilter(difficulty="Beginner")
        result = apply_metadata_filters(self.sample_results, filter_obj)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 'recipe1')
    
    def test_time_range_filter(self):
        """Test time range filtering."""
        filter_obj = RecipeFilter(prep_time_max=20)
        result = apply_metadata_filters(self.sample_results, filter_obj)
        self.assertEqual(len(result), 1)  # Only recipe1 has prep_time <= 20
    
    def test_combined_filters(self):
        """Test multiple filters together."""
        filter_obj = RecipeFilter(difficulty="Beginner", servings_max=5)
        result = apply_metadata_filters(self.sample_results, filter_obj)
        self.assertEqual(len(result), 1)  # Only recipe1 matches both


class TestVectorStoreIntegration(unittest.TestCase):
    """Test filtering integration with VectorRecipeStore."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.store = VectorRecipeStore()
    
    @patch('src.vector.store.VectorRecipeStore.collection')
    @patch('src.vector.store.create_search_embedding')
    def test_search_with_filters(self, mock_embedding, mock_collection):
        """Test search methods with filters."""
        # Mock embedding and collection response
        mock_embedding.return_value = [0.1] * 1536
        mock_collection.query.return_value = {
            'ids': [['recipe1']],
            'distances': [[0.2]],
            'metadatas': [[{'title': 'Test Recipe', 'difficulty': 'Beginner'}]],
            'documents': [['test doc']]
        }
        
        filters = RecipeFilter(difficulty="Beginner")
        results = self.store.search_recipes("test", filters=filters)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['metadata']['difficulty'], 'Beginner')


if __name__ == '__main__':
    unittest.main()