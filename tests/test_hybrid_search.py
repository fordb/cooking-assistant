"""
Tests for hybrid search functionality combining sparse and dense search.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Union

from src.vector.store import VectorRecipeStore


class TestHybridSearch(unittest.TestCase):
    """Test hybrid search functionality in VectorRecipeStore."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock sparse search results
        self.mock_sparse_results = [
            {
                'recipe': {'title': 'Chicken Fried Rice', 'ingredients': ['rice', 'chicken']},
                'recipe_id': 'recipe1',
                'score': 7.5,
                'search_type': 'sparse'
            },
            {
                'recipe': {'title': 'Vegetable Curry', 'ingredients': ['vegetables', 'curry powder']},
                'recipe_id': 'recipe2', 
                'score': 5.2,
                'search_type': 'sparse'
            },
            {
                'recipe': {'title': 'Beef Stir Fry', 'ingredients': ['beef', 'vegetables']},
                'recipe_id': 'recipe3',
                'score': 3.8,
                'search_type': 'sparse'
            }
        ]
        
        # Mock dense search results
        self.mock_dense_results = [
            {
                'id': 'recipe1',  # Overlapping with sparse
                'similarity': 0.85,
                'metadata': {'title': 'Chicken Fried Rice', 'ingredients': ['rice', 'chicken']},
                'document': 'Chicken Fried Rice recipe...'
            },
            {
                'id': 'recipe4',  # Only in dense search
                'similarity': 0.78,
                'metadata': {'title': 'Thai Chicken Curry', 'ingredients': ['chicken', 'curry']},
                'document': 'Thai Chicken Curry recipe...'
            },
            {
                'id': 'recipe2',  # Overlapping with sparse
                'similarity': 0.72,
                'metadata': {'title': 'Vegetable Curry', 'ingredients': ['vegetables', 'curry powder']},
                'document': 'Vegetable Curry recipe...'
            }
        ]
    
    @patch('chromadb.HttpClient')
    def test_rrf_algorithm_implementation(self, mock_client):
        """Test the Reciprocal Rank Fusion (RRF) algorithm implementation."""
        # Mock Chroma client setup
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        store = VectorRecipeStore()
        
        # Test RRF with known values
        sparse_weight = 0.4
        dense_weight = 0.6
        rrf_k = 60
        n_results = 5
        
        # Mock the config values
        store.config.RRF_K = rrf_k
        
        combined_results = store._combine_search_results(
            self.mock_sparse_results, self.mock_dense_results,
            sparse_weight, dense_weight, n_results
        )
        
        # Verify results structure
        self.assertIsInstance(combined_results, list)
        self.assertLessEqual(len(combined_results), n_results)
        
        # Verify result format
        for result in combined_results:
            self.assertIn('recipe', result)
            self.assertIn('recipe_id', result)
            self.assertIn('sparse_score', result)
            self.assertIn('dense_score', result)
            self.assertIn('rrf_sparse', result)
            self.assertIn('rrf_dense', result)
            self.assertIn('combined_score', result)
            self.assertEqual(result['search_type'], 'hybrid')
        
        # Verify RRF scoring calculation for overlapping results
        recipe1_result = next((r for r in combined_results if r['recipe_id'] == 'recipe1'), None)
        self.assertIsNotNone(recipe1_result)
        
        # recipe1 is rank 1 in both sparse and dense, so:
        # rrf_sparse = 0.4 / (60 + 1) = 0.00656...
        # rrf_dense = 0.6 / (60 + 1) = 0.00984...
        # combined = 0.00656 + 0.00984 = 0.0164...
        expected_rrf_sparse = sparse_weight / (rrf_k + 1)
        expected_rrf_dense = dense_weight / (rrf_k + 1) 
        expected_combined = expected_rrf_sparse + expected_rrf_dense
        
        self.assertAlmostEqual(recipe1_result['rrf_sparse'], expected_rrf_sparse, places=4)
        self.assertAlmostEqual(recipe1_result['rrf_dense'], expected_rrf_dense, places=4)
        self.assertAlmostEqual(recipe1_result['combined_score'], expected_combined, places=4)
    
    @patch('chromadb.HttpClient')
    def test_hybrid_search_with_overlapping_results(self, mock_client):
        """Test hybrid search handles overlapping results correctly."""
        # Mock Chroma client setup
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        store = VectorRecipeStore()
        
        # Ensure hybrid search is enabled for this test
        store.config.HYBRID_ENABLED = True
        
        # Mock the search methods to return our test data
        store.search_recipes_sparse = Mock(return_value=self.mock_sparse_results)
        store.search_recipes = Mock(return_value=self.mock_dense_results)
        
        # Test hybrid search
        results = store.search_recipes_hybrid("chicken curry", n_results=5)
        
        # Verify both search methods were called
        store.search_recipes_sparse.assert_called_once()
        store.search_recipes.assert_called_once()
        
        # Verify results format
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Check that overlapping results (recipe1, recipe2) have combined scores
        recipe1_result = next((r for r in results if r['recipe_id'] == 'recipe1'), None)
        recipe2_result = next((r for r in results if r['recipe_id'] == 'recipe2'), None)
        
        self.assertIsNotNone(recipe1_result)
        self.assertIsNotNone(recipe2_result)
        
        # These should have both sparse and dense scores > 0
        self.assertGreater(recipe1_result['sparse_score'], 0)
        self.assertGreater(recipe1_result['dense_score'], 0)
        self.assertGreater(recipe2_result['sparse_score'], 0)
        self.assertGreater(recipe2_result['dense_score'], 0)
        
        # Check that non-overlapping results have zero for missing search type
        recipe3_result = next((r for r in results if r['recipe_id'] == 'recipe3'), None)
        recipe4_result = next((r for r in results if r['recipe_id'] == 'recipe4'), None)
        
        if recipe3_result:  # Only in sparse
            self.assertGreater(recipe3_result['sparse_score'], 0)
            self.assertEqual(recipe3_result['dense_score'], 0)
        
        if recipe4_result:  # Only in dense
            self.assertEqual(recipe4_result['sparse_score'], 0)
            self.assertGreater(recipe4_result['dense_score'], 0)
    
    @patch('chromadb.HttpClient')
    def test_hybrid_search_with_no_sparse_results(self, mock_client):
        """Test hybrid search when sparse search returns no results."""
        # Mock Chroma client setup
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        store = VectorRecipeStore()
        
        # Ensure hybrid search is enabled for this test
        store.config.HYBRID_ENABLED = True
        
        # Mock sparse search to return empty, dense search to return results
        store.search_recipes_sparse = Mock(return_value=[])
        store.search_recipes = Mock(return_value=self.mock_dense_results)
        
        results = store.search_recipes_hybrid("test query", n_results=5)
        
        # Should still return results from dense search only
        self.assertGreater(len(results), 0)
        
        # All results should have sparse_score = 0, dense_score > 0
        for result in results:
            self.assertEqual(result['sparse_score'], 0)
            self.assertGreaterEqual(result['dense_score'], 0)
            self.assertEqual(result['rrf_sparse'], 0)
            self.assertGreater(result['rrf_dense'], 0)
    
    @patch('chromadb.HttpClient')
    def test_hybrid_search_with_no_dense_results(self, mock_client):
        """Test hybrid search when dense search returns no results."""
        # Mock Chroma client setup
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        store = VectorRecipeStore()
        
        # Ensure hybrid search is enabled for this test
        store.config.HYBRID_ENABLED = True
        
        # Mock dense search to return empty, sparse search to return results
        store.search_recipes_sparse = Mock(return_value=self.mock_sparse_results)
        store.search_recipes = Mock(return_value=[])
        
        results = store.search_recipes_hybrid("test query", n_results=5)
        
        # Should still return results from sparse search only
        self.assertGreater(len(results), 0)
        
        # All results should have dense_score = 0, sparse_score > 0
        for result in results:
            self.assertGreater(result['sparse_score'], 0)
            self.assertEqual(result['dense_score'], 0)
            self.assertGreater(result['rrf_sparse'], 0)
            self.assertEqual(result['rrf_dense'], 0)
    
    @patch('chromadb.HttpClient')
    def test_hybrid_search_with_no_results(self, mock_client):
        """Test hybrid search when both searches return no results."""
        # Mock Chroma client setup
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        store = VectorRecipeStore()
        
        # Mock both searches to return empty results
        store.search_recipes_sparse = Mock(return_value=[])
        store.search_recipes = Mock(return_value=[])
        
        results = store.search_recipes_hybrid("nonexistent query", n_results=5)
        
        # Should return empty list
        self.assertEqual(len(results), 0)
    
    @patch('chromadb.HttpClient')
    def test_hybrid_search_custom_weights(self, mock_client):
        """Test hybrid search with custom sparse/dense weights."""
        # Mock Chroma client setup
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        store = VectorRecipeStore()
        
        # Mock the search methods
        store.search_recipes_sparse = Mock(return_value=self.mock_sparse_results)
        store.search_recipes = Mock(return_value=self.mock_dense_results)
        
        # Test with custom weights favoring sparse search
        sparse_weight = 0.8
        dense_weight = 0.2
        
        results = store.search_recipes_hybrid(
            "test query", n_results=5,
            sparse_weight=sparse_weight, dense_weight=dense_weight
        )
        
        # Verify results were returned
        self.assertGreater(len(results), 0)
        
        # Check that overlapping result has correct weight calculations
        recipe1_result = next((r for r in results if r['recipe_id'] == 'recipe1'), None)
        self.assertIsNotNone(recipe1_result)
        
        # Verify the RRF calculations use custom weights
        expected_rrf_sparse = sparse_weight / (store.config.RRF_K + 1)
        expected_rrf_dense = dense_weight / (store.config.RRF_K + 1)
        
        self.assertAlmostEqual(recipe1_result['rrf_sparse'], expected_rrf_sparse, places=4)
        self.assertAlmostEqual(recipe1_result['rrf_dense'], expected_rrf_dense, places=4)
    
    @patch('chromadb.HttpClient')
    def test_hybrid_search_disabled(self, mock_client):
        """Test hybrid search when disabled in configuration."""
        # Mock Chroma client setup
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        store = VectorRecipeStore()
        
        # Disable hybrid search in config
        store.config.HYBRID_ENABLED = False
        
        results = store.search_recipes_hybrid("test query", n_results=5)
        
        # Should return empty results when disabled
        self.assertEqual(len(results), 0)
    
    @patch('chromadb.HttpClient')
    def test_hybrid_search_result_ordering(self, mock_client):
        """Test that hybrid search results are ordered by combined score."""
        # Mock Chroma client setup
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        store = VectorRecipeStore()
        
        # Mock the search methods
        store.search_recipes_sparse = Mock(return_value=self.mock_sparse_results)
        store.search_recipes = Mock(return_value=self.mock_dense_results)
        
        results = store.search_recipes_hybrid("test query", n_results=10)
        
        # Verify results are ordered by combined_score (descending)
        combined_scores = [result['combined_score'] for result in results]
        sorted_scores = sorted(combined_scores, reverse=True)
        
        self.assertEqual(combined_scores, sorted_scores)
    
    @patch('chromadb.HttpClient')
    def test_hybrid_search_fallback_on_error(self, mock_client):
        """Test hybrid search falls back to dense search on errors."""
        # Mock Chroma client setup
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        store = VectorRecipeStore()
        
        # Ensure hybrid search is enabled for this test
        store.config.HYBRID_ENABLED = True
        
        # Mock sparse search to raise an exception
        store.search_recipes_sparse = Mock(side_effect=Exception("Sparse search failed"))
        store.search_recipes = Mock(return_value=self.mock_dense_results)
        
        results = store.search_recipes_hybrid("test query", n_results=5)
        
        # Should fall back to dense search results
        self.assertGreater(len(results), 0)
        
        # Verify dense search was called for fallback
        store.search_recipes.assert_called()


if __name__ == '__main__':
    unittest.main()