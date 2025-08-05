"""
Tests for recipe filtering functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Union

from src.vector.filters import (
    RecipeFilter, create_recipe_filter, apply_metadata_filters, 
    validate_filter_ranges, FilterValidationError
)
from src.vector.store import VectorRecipeStore

# Type definitions
RecipeMetadata = Dict[str, Union[str, int, List[str]]]
SearchResult = Dict[str, Union[str, float, RecipeMetadata]]


class TestRecipeFilter(unittest.TestCase):
    """Test RecipeFilter class and validation."""
    
    def test_recipe_filter_creation_valid(self):
        """Test creating valid RecipeFilter objects."""
        # Basic filter
        filter1 = RecipeFilter(difficulty="Beginner")
        self.assertEqual(filter1.difficulty, "Beginner")
        self.assertTrue(filter1.has_filters())
        
        # Range filter
        filter2 = RecipeFilter(prep_time_min=10, prep_time_max=30)
        self.assertEqual(filter2.prep_time_min, 10)
        self.assertEqual(filter2.prep_time_max, 30)
        
        # Dietary restrictions
        filter3 = RecipeFilter(dietary_restrictions=["vegetarian", "gluten-free"])
        self.assertEqual(len(filter3.dietary_restrictions), 2)
        
        # Complex filter
        filter4 = RecipeFilter(
            difficulty="Intermediate",
            prep_time_min=15,
            cook_time_max=45,
            servings_min=4,
            servings_max=8,
            dietary_restrictions=["vegetarian"],
            max_total_time=60
        )
        self.assertTrue(filter4.has_filters())
    
    def test_recipe_filter_invalid_difficulty(self):
        """Test validation of invalid difficulty levels."""
        with self.assertRaises(FilterValidationError):
            RecipeFilter(difficulty="Expert")  # Not in supported list
    
    def test_recipe_filter_invalid_ranges(self):
        """Test validation of invalid range filters."""
        # Min greater than max
        with self.assertRaises(FilterValidationError):
            RecipeFilter(prep_time_min=60, prep_time_max=30)
        
        with self.assertRaises(FilterValidationError):
            RecipeFilter(cook_time_min=120, cook_time_max=60)
        
        with self.assertRaises(FilterValidationError):
            RecipeFilter(servings_min=8, servings_max=4)
        
        # Values outside valid ranges
        with self.assertRaises(FilterValidationError):
            RecipeFilter(prep_time_min=-5)
        
        with self.assertRaises(FilterValidationError):
            RecipeFilter(servings_max=100)  # Above MAX_SERVINGS_FILTER
    
    def test_recipe_filter_invalid_dietary_restrictions(self):
        """Test validation of invalid dietary restrictions."""
        with self.assertRaises(FilterValidationError):
            RecipeFilter(dietary_restrictions=["invalid-diet"])
    
    def test_recipe_filter_no_filters(self):
        """Test empty filter detection."""
        empty_filter = RecipeFilter()
        self.assertFalse(empty_filter.has_filters())
    
    def test_recipe_filter_to_dict(self):
        """Test filter dictionary conversion."""
        filter_obj = RecipeFilter(
            difficulty="Beginner",
            prep_time_min=10,
            prep_time_max=30,
            dietary_restrictions=["vegetarian"]
        )
        
        result = filter_obj.to_dict()
        self.assertEqual(result['difficulty'], "Beginner")
        self.assertEqual(result['prep_time_range'], "10-30")
        self.assertEqual(result['dietary_restrictions'], ["vegetarian"])


class TestCreateRecipeFilter(unittest.TestCase):
    """Test the create_recipe_filter convenience function."""
    
    def test_create_recipe_filter_valid(self):
        """Test creating filters through convenience function."""
        filter_obj = create_recipe_filter(
            difficulty="Intermediate",
            prep_time_min=15,
            cook_time_max=60,
            servings_min=2,
            dietary_restrictions=["vegan"]
        )
        
        self.assertEqual(filter_obj.difficulty, "Intermediate")
        self.assertEqual(filter_obj.prep_time_min, 15)
        self.assertEqual(filter_obj.cook_time_max, 60)
        self.assertEqual(filter_obj.servings_min, 2)
        self.assertEqual(filter_obj.dietary_restrictions, ["vegan"])
    
    def test_create_recipe_filter_invalid(self):
        """Test error handling in convenience function."""
        with self.assertRaises(FilterValidationError):
            create_recipe_filter(difficulty="Invalid")


class TestValidateFilterRanges(unittest.TestCase):
    """Test filter range validation."""
    
    def test_validate_filter_ranges_valid(self):
        """Test validation of valid ranges."""
        # Valid ranges should return True
        self.assertTrue(validate_filter_ranges(
            prep_time_range=(10, 30),
            cook_time_range=(15, 45),
            servings_range=(2, 8)
        ))
    
    def test_validate_filter_ranges_invalid(self):
        """Test validation of invalid ranges."""
        # Min > Max
        with self.assertRaises(FilterValidationError):
            validate_filter_ranges(prep_time_range=(30, 10))
        
        # Out of bounds
        with self.assertRaises(FilterValidationError):
            validate_filter_ranges(prep_time_range=(-10, 30))
        
        with self.assertRaises(FilterValidationError):
            validate_filter_ranges(servings_range=(1, 100))


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
                    'servings': 4,
                    'ingredients': ['chicken breast', 'vegetables', 'soy sauce']
                }
            },
            {
                'id': 'recipe2', 
                'metadata': {
                    'title': 'Vegetable Curry',
                    'difficulty': 'Intermediate',
                    'prep_time': 20,
                    'cook_time': 30,
                    'servings': 6,
                    'ingredients': ['mixed vegetables', 'curry powder', 'coconut milk']
                }
            },
            {
                'id': 'recipe3',
                'metadata': {
                    'title': 'Beef Stew',
                    'difficulty': 'Advanced',
                    'prep_time': 30,
                    'cook_time': 120,
                    'servings': 8,
                    'ingredients': ['beef chunks', 'potatoes', 'carrots']
                }
            }
        ]
    
    def test_apply_no_filters(self):
        """Test that no filters returns original results."""
        no_filter = RecipeFilter()
        result = apply_metadata_filters(self.sample_results, no_filter)
        self.assertEqual(len(result), 3)
        self.assertEqual(result, self.sample_results)
        
        # Test with None filter
        result = apply_metadata_filters(self.sample_results, None)
        self.assertEqual(len(result), 3)
    
    def test_apply_difficulty_filter(self):
        """Test difficulty filtering."""
        # Filter for Beginner recipes
        filter_obj = RecipeFilter(difficulty="Beginner")
        result = apply_metadata_filters(self.sample_results, filter_obj)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 'recipe1')
        
        # Filter for Advanced recipes
        filter_obj = RecipeFilter(difficulty="Advanced")
        result = apply_metadata_filters(self.sample_results, filter_obj)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 'recipe3')
    
    def test_apply_prep_time_filter(self):
        """Test prep time range filtering."""
        # Filter for prep time <= 20 minutes
        filter_obj = RecipeFilter(prep_time_max=20)
        result = apply_metadata_filters(self.sample_results, filter_obj)
        
        self.assertEqual(len(result), 2)  # recipe1 (15) and recipe2 (20)
        
        # Filter for prep time >= 20 minutes
        filter_obj = RecipeFilter(prep_time_min=20)
        result = apply_metadata_filters(self.sample_results, filter_obj)
        
        self.assertEqual(len(result), 2)  # recipe2 (20) and recipe3 (30)
        
        # Filter for prep time range 15-25 minutes
        filter_obj = RecipeFilter(prep_time_min=15, prep_time_max=25)
        result = apply_metadata_filters(self.sample_results, filter_obj)
        
        self.assertEqual(len(result), 2)  # recipe1 (15) and recipe2 (20)
    
    def test_apply_cook_time_filter(self):
        """Test cook time range filtering."""
        # Filter for cook time <= 30 minutes
        filter_obj = RecipeFilter(cook_time_max=30)
        result = apply_metadata_filters(self.sample_results, filter_obj)
        
        self.assertEqual(len(result), 2)  # recipe1 (10) and recipe2 (30)
    
    def test_apply_servings_filter(self):
        """Test servings range filtering."""
        # Filter for servings <= 6
        filter_obj = RecipeFilter(servings_max=6)
        result = apply_metadata_filters(self.sample_results, filter_obj)
        
        self.assertEqual(len(result), 2)  # recipe1 (4) and recipe2 (6)
        
        # Filter for servings >= 6
        filter_obj = RecipeFilter(servings_min=6)
        result = apply_metadata_filters(self.sample_results, filter_obj)
        
        self.assertEqual(len(result), 2)  # recipe2 (6) and recipe3 (8)
    
    def test_apply_max_total_time_filter(self):
        """Test max total time filtering."""
        # Filter for total time <= 50 minutes
        filter_obj = RecipeFilter(max_total_time=50)
        result = apply_metadata_filters(self.sample_results, filter_obj)
        
        self.assertEqual(len(result), 2)  # recipe1 (25 total) and recipe2 (50 total)
    
    def test_apply_dietary_restrictions_filter(self):
        """Test dietary restrictions filtering."""
        # Filter for vegetarian (simple keyword matching)
        filter_obj = RecipeFilter(dietary_restrictions=["vegetarian"])
        result = apply_metadata_filters(self.sample_results, filter_obj)
        
        # Should match recipe2 (Vegetable Curry) based on keyword matching
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 'recipe2')
    
    def test_apply_combined_filters(self):
        """Test applying multiple filters together."""
        # Filter for Beginner recipes with prep time <= 20 and servings <= 5
        filter_obj = RecipeFilter(
            difficulty="Beginner",
            prep_time_max=20,
            servings_max=5
        )
        result = apply_metadata_filters(self.sample_results, filter_obj)
        
        self.assertEqual(len(result), 1)  # Only recipe1 matches all criteria
        self.assertEqual(result[0]['id'], 'recipe1')
    
    def test_apply_filters_no_matches(self):
        """Test filters that result in no matches."""
        # Filter for impossible combination
        filter_obj = RecipeFilter(
            difficulty="Beginner",
            prep_time_min=60  # No beginner recipes take 60+ min prep
        )
        result = apply_metadata_filters(self.sample_results, filter_obj)
        
        self.assertEqual(len(result), 0)
    
    def test_apply_filters_sparse_result_format(self):
        """Test filtering with sparse search result format."""
        sparse_results = [
            {
                'recipe_id': 'recipe1',
                'recipe': {  # Different key name for sparse results
                    'title': 'Quick Pasta',
                    'difficulty': 'Beginner',
                    'prep_time': 10,
                    'cook_time': 15,
                    'servings': 2
                },
                'score': 5.2
            }
        ]
        
        filter_obj = RecipeFilter(difficulty="Beginner")
        result = apply_metadata_filters(sparse_results, filter_obj)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['recipe_id'], 'recipe1')
    
    def test_apply_filters_invalid_metadata(self):
        """Test filtering with invalid or missing metadata."""
        invalid_results = [
            {'id': 'recipe1'},  # No metadata
            {
                'id': 'recipe2',
                'metadata': {
                    'title': 'Recipe with missing fields',
                    'difficulty': 'Beginner'
                    # Missing prep_time, cook_time, servings
                }
            }
        ]
        
        filter_obj = RecipeFilter(prep_time_max=30)
        result = apply_metadata_filters(invalid_results, filter_obj)
        
        # Should handle gracefully and skip invalid entries
        self.assertEqual(len(result), 0)


class TestVectorStoreFilteringIntegration(unittest.TestCase):
    """Test filtering integration with VectorRecipeStore methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.store = VectorRecipeStore()
    
    @patch('src.vector.store.VectorRecipeStore.collection')
    @patch('src.vector.store.create_search_embedding')
    def test_dense_search_with_filters(self, mock_embedding, mock_collection):
        """Test dense search with filters applied."""
        # Mock embedding generation
        mock_embedding.return_value = [0.1] * 1536
        
        # Mock collection query response
        mock_collection.query.return_value = {
            'ids': [['recipe1', 'recipe2']],
            'distances': [[0.2, 0.3]],
            'metadatas': [[
                {'title': 'Chicken Soup', 'difficulty': 'Beginner', 'prep_time': 15},
                {'title': 'Beef Stew', 'difficulty': 'Advanced', 'prep_time': 30}
            ]],
            'documents': [['doc1', 'doc2']]
        }
        
        # Create filter for Beginner recipes only
        filters = RecipeFilter(difficulty="Beginner")
        
        # Perform search with filters
        results = self.store.search_recipes("soup", filters=filters)
        
        # Should only return the Beginner recipe
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['metadata']['difficulty'], 'Beginner')
    
    def test_sparse_search_with_filters(self):
        """Test sparse search with filters applied."""
        import numpy as np
        
        # Mock the BM25 index and data directly
        mock_index = Mock()
        # Return numpy array for argsort compatibility
        mock_index.get_scores.return_value = np.array([2.5, 1.8])
        
        self.store._bm25_index = mock_index
        self.store._bm25_recipes = [
            {'title': 'Quick Pasta', 'difficulty': 'Beginner', 'prep_time': 10},
            {'title': 'Slow Roast', 'difficulty': 'Advanced', 'prep_time': 45}
        ]
        self.store._bm25_recipe_ids = ['recipe1', 'recipe2']
        
        # Mock the keyword extraction
        with patch('src.vector.store.extract_query_keywords') as mock_extract:
            mock_extract.return_value = ['pasta']
            
            # Create filter for prep time <= 20 minutes
            filters = RecipeFilter(prep_time_max=20)
            
            # Perform search with filters
            results = self.store.search_recipes_sparse("pasta", filters=filters)
            
            # Should only return the quick recipe
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['recipe']['title'], 'Quick Pasta')
    
    @patch('src.vector.store.VectorRecipeStore.search_recipes_sparse')
    @patch('src.vector.store.VectorRecipeStore.search_recipes')
    def test_hybrid_search_with_filters(self, mock_dense, mock_sparse):
        """Test hybrid search passes filters to component searches."""
        # Mock component search results
        mock_sparse.return_value = [
            {'recipe_id': 'recipe1', 'recipe': {'title': 'Pasta'}, 'score': 2.0}
        ]
        mock_dense.return_value = [
            {'id': 'recipe1', 'metadata': {'title': 'Pasta'}, 'similarity': 0.8}
        ]
        
        # Create filter
        filters = RecipeFilter(difficulty="Beginner")
        
        # Perform hybrid search
        self.store.search_recipes_hybrid("pasta", filters=filters)
        
        # Verify filters were passed to component searches
        mock_sparse.assert_called_with("pasta", n_results=20, filters=filters)
        mock_dense.assert_called_with("pasta", n_results=20, filters=filters)


if __name__ == '__main__':
    unittest.main()