"""
Tests for sparse search functionality using BM25.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import List

from src.recipes.models import Recipe
from src.vector.keywords import (
    extract_recipe_keywords, extract_query_keywords, 
    build_recipe_corpus, tokenize_text
)
from src.vector.store import VectorRecipeStore


class TestKeywordExtraction(unittest.TestCase):
    """Test keyword extraction utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_recipe = Recipe(
            title="Chicken Fried Rice",
            prep_time=15,
            cook_time=12,
            servings=4,
            difficulty="Beginner",
            ingredients=["2 cups cooked rice", "1 chicken breast", "2 eggs", "soy sauce"],
            instructions=["Cook chicken", "Add rice and eggs", "Season with soy sauce"]
        )
    
    def test_tokenize_text(self):
        """Test text tokenization."""
        text = "Chicken, fried rice with soy-sauce!"
        tokens = tokenize_text(text)
        
        expected = ["chicken", "fried", "rice", "with", "soy", "sauce"]
        self.assertEqual(tokens, expected)
    
    def test_tokenize_empty_text(self):
        """Test tokenization of empty text."""
        tokens = tokenize_text("")
        self.assertEqual(tokens, [])
    
    def test_extract_recipe_keywords(self):
        """Test keyword extraction from recipe."""
        keywords = extract_recipe_keywords(self.test_recipe)
        
        # Should contain keywords from title, ingredients, and instructions
        self.assertIn("chicken", keywords)
        self.assertIn("fried", keywords)
        self.assertIn("rice", keywords)
        self.assertIn("eggs", keywords)
        self.assertIn("cook", keywords)
        
        # Should not contain short words or stopwords
        self.assertNotIn("a", keywords)
        self.assertNotIn("with", keywords)
        
        # Title should appear multiple times (weighted)
        title_count = keywords.count("chicken") + keywords.count("fried")
        self.assertGreater(title_count, 2)  # Title words appear multiple times
    
    def test_extract_query_keywords(self):
        """Test keyword extraction from search query."""
        query = "quick chicken dinner recipe"
        keywords = extract_query_keywords(query)
        
        self.assertIn("quick", keywords)
        self.assertIn("chicken", keywords)
        self.assertIn("dinner", keywords)
        self.assertIn("recipe", keywords)
        self.assertEqual(len(keywords), 4)
    
    def test_extract_query_keywords_with_stopwords(self):
        """Test query keyword extraction filters stopwords."""
        query = "a quick chicken recipe for dinner"
        keywords = extract_query_keywords(query)
        
        # Should include meaningful words
        self.assertIn("quick", keywords)
        self.assertIn("chicken", keywords)
        self.assertIn("recipe", keywords)
        self.assertIn("dinner", keywords)
        
        # Should exclude stopwords
        self.assertNotIn("a", keywords)
        self.assertNotIn("for", keywords)
    
    def test_build_recipe_corpus(self):
        """Test building BM25 corpus from recipes."""
        recipes = [
            self.test_recipe,
            Recipe(
                title="Vegetable Curry",
                prep_time=20,
                cook_time=25,
                servings=4,
                difficulty="Intermediate",
                ingredients=["vegetables", "curry powder", "coconut milk"],
                instructions=["Sauté vegetables", "Add curry powder", "Add coconut milk"]
            )
        ]
        
        corpus = build_recipe_corpus(recipes)
        
        self.assertEqual(len(corpus), 2)
        self.assertIsInstance(corpus[0], list)
        self.assertIsInstance(corpus[1], list)
        
        # First recipe corpus should contain chicken keywords
        self.assertIn("chicken", corpus[0])
        self.assertIn("fried", corpus[0])
        
        # Second recipe corpus should contain curry keywords
        self.assertIn("vegetable", corpus[1])
        self.assertIn("curry", corpus[1])


class TestSparseSearch(unittest.TestCase):
    """Test sparse search functionality in VectorRecipeStore."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_recipes = [
            Recipe(
                title="Chicken Fried Rice",
                prep_time=15,
                cook_time=12,
                servings=4,
                difficulty="Beginner",
                ingredients=["2 cups cooked rice", "1 chicken breast", "2 eggs"],
                instructions=["Cook chicken", "Add rice and eggs", "Stir fry together"]
            ),
            Recipe(
                title="Vegetable Curry",
                prep_time=20,
                cook_time=25,
                servings=4,
                difficulty="Intermediate",
                ingredients=["mixed vegetables", "curry powder", "coconut milk"],
                instructions=["Sauté vegetables", "Add spices", "Simmer in coconut milk"]
            ),
            Recipe(
                title="Chicken Curry",
                prep_time=25,
                cook_time=30,
                servings=6,
                difficulty="Intermediate",
                ingredients=["chicken thighs", "curry powder", "tomatoes"],
                instructions=["Brown chicken", "Add curry spices", "Simmer with tomatoes"]
            )
        ]
    
    @patch('chromadb.HttpClient')
    def test_bm25_index_building(self, mock_client):
        """Test BM25 index building from collection data."""
        # Mock Chroma client and collection
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        # Mock collection data
        mock_collection.get.return_value = {
            'ids': ['recipe1', 'recipe2'],
            'metadatas': [
                {
                    'title': 'Chicken Fried Rice',
                    'prep_time': 15,
                    'cook_time': 12,
                    'servings': 4,
                    'difficulty': 'Beginner',
                    'ingredients': ['rice', 'chicken', 'eggs'],
                    'instructions': ['cook chicken', 'add rice', 'stir and serve']
                },
                {
                    'title': 'Vegetable Curry',
                    'prep_time': 20,
                    'cook_time': 25,
                    'servings': 4,
                    'difficulty': 'Intermediate',
                    'ingredients': ['vegetables', 'curry powder'],
                    'instructions': ['cook vegetables', 'add spices', 'simmer and serve']
                }
            ]
        }
        
        store = VectorRecipeStore()
        store._build_bm25_index()
        
        # Verify BM25 index was built
        self.assertIsNotNone(store._bm25_index)
        self.assertEqual(len(store._bm25_recipes), 2)
        self.assertEqual(len(store._bm25_recipe_ids), 2)
    
    @patch('chromadb.HttpClient')
    def test_sparse_search_functionality(self, mock_client):
        """Test sparse search with keyword matching."""
        # Mock Chroma client setup
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        # Mock collection data with chicken and curry recipes
        mock_collection.get.return_value = {
            'ids': ['recipe1', 'recipe2', 'recipe3'],
            'metadatas': [
                {
                    'title': 'Chicken Fried Rice',
                    'prep_time': 15,
                    'cook_time': 12,
                    'servings': 4,
                    'difficulty': 'Beginner',
                    'ingredients': ['rice', 'chicken breast', 'eggs'],
                    'instructions': ['cook chicken', 'fry rice', 'mix together']
                },
                {
                    'title': 'Vegetable Curry',
                    'prep_time': 20,
                    'cook_time': 25,
                    'servings': 4,
                    'difficulty': 'Intermediate',
                    'ingredients': ['mixed vegetables', 'curry powder'],
                    'instructions': ['cook vegetables', 'add curry spices', 'simmer until done']
                },
                {
                    'title': 'Chicken Curry',
                    'prep_time': 25,
                    'cook_time': 30,
                    'servings': 6,
                    'difficulty': 'Intermediate',
                    'ingredients': ['chicken thighs', 'curry powder'],
                    'instructions': ['brown chicken', 'add curry', 'cook until tender']
                }
            ]
        }
        
        store = VectorRecipeStore()
        
        # Test search for "chicken" - should find chicken recipes
        chicken_results = store.search_recipes_sparse("chicken", n_results=3)
        
        self.assertGreater(len(chicken_results), 0)
        
        # Check that results contain chicken recipes
        chicken_titles = [result['recipe'].get('title', '') for result in chicken_results]
        self.assertTrue(any('Chicken' in title for title in chicken_titles))
        
        # Test search for "curry" - should find curry recipes  
        curry_results = store.search_recipes_sparse("curry spices", n_results=3)
        
        self.assertGreater(len(curry_results), 0)
        
        # Check that results contain curry recipes
        curry_titles = [result['recipe'].get('title', '') for result in curry_results]
        self.assertTrue(any('Curry' in title for title in curry_titles))
    
    @patch('chromadb.HttpClient')
    def test_sparse_search_no_results(self, mock_client):
        """Test sparse search with no matching keywords."""
        # Mock Chroma client setup
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        # Mock empty collection
        mock_collection.get.return_value = {
            'ids': [],
            'metadatas': []
        }
        
        store = VectorRecipeStore()
        results = store.search_recipes_sparse("nonexistent ingredients", n_results=5)
        
        self.assertEqual(len(results), 0)
    
    @patch('chromadb.HttpClient')
    def test_sparse_search_empty_query(self, mock_client):
        """Test sparse search with empty query."""
        # Mock Chroma client setup  
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        store = VectorRecipeStore()
        results = store.search_recipes_sparse("", n_results=5)
        
        self.assertEqual(len(results), 0)
    
    @patch('chromadb.HttpClient') 
    def test_sparse_search_result_format(self, mock_client):
        """Test that sparse search results have correct format."""
        # Mock Chroma client setup
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        # Mock collection with one recipe
        mock_collection.get.return_value = {
            'ids': ['recipe1'],
            'metadatas': [{
                'title': 'Test Recipe',
                'prep_time': 10,
                'cook_time': 15,
                'servings': 2,
                'difficulty': 'Easy',
                'ingredients': ['test ingredient'],
                'instructions': ['test instruction', 'continue cooking', 'serve hot']
            }]
        }
        
        store = VectorRecipeStore()
        results = store.search_recipes_sparse("test", n_results=1)
        
        if results:  # Only test if we got results
            result = results[0]
            
            # Check result structure
            self.assertIn('recipe', result)
            self.assertIn('recipe_id', result)
            self.assertIn('score', result)
            self.assertIn('search_type', result)
            
            # Check result values
            self.assertIsInstance(result['recipe'], dict)  # Now returns metadata dict
            self.assertEqual(result['search_type'], 'sparse')
            self.assertIsInstance(result['score'], float)
            self.assertGreaterEqual(result['score'], 0)


if __name__ == '__main__':
    unittest.main()