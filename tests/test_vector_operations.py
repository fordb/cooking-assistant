"""
Tests for vector database operations.
Tests embedding generation, vector store operations, and recipe ingestion.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import uuid
from typing import List

from src.models import Recipe
from src.vector_embeddings import RecipeEmbeddingGenerator, create_search_embedding
from src.vector_store import VectorRecipeStore, VectorStoreError
from src.recipe_ingestion import RecipeIngestionPipeline
from src.exceptions import EmbeddingGenerationError

class TestRecipeEmbeddingGenerator(unittest.TestCase):
    """Test recipe embedding generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_recipe = Recipe(
            title="Test Chicken Rice",
            prep_time=15,
            cook_time=25,
            servings=4,
            difficulty="Beginner",
            ingredients=["2 cups rice", "1 lb chicken breast", "Salt to taste"],
            instructions=["Cook rice in pot", "Season chicken thoroughly", "Combine and serve hot"]
        )
        
    def test_recipe_text_preparation(self):
        """Test recipe text preparation for embedding."""
        generator = RecipeEmbeddingGenerator()
        text = generator.prepare_recipe_text(self.sample_recipe)
        
        # Check that all key components are included
        self.assertIn("Test Chicken Rice", text)
        self.assertIn("Beginner", text)
        self.assertIn("15 minutes prep", text)
        self.assertIn("25 minutes cook", text)
        self.assertIn("Serves 4", text)
        self.assertIn("2 cups rice", text)
        self.assertIn("Cook rice", text)
        
        # Check text structure
        self.assertIn("Recipe:", text)
        self.assertIn("Ingredients:", text)
        self.assertIn("Instructions:", text)
    
    @patch('openai.embeddings.create')
    def test_embedding_generation(self, mock_create):
        """Test OpenAI embedding generation."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = [0.1, 0.2, 0.3, 0.4]
        mock_create.return_value = mock_response
        
        generator = RecipeEmbeddingGenerator()
        embedding = generator.generate_embedding("test text")
        
        self.assertEqual(embedding, [0.1, 0.2, 0.3, 0.4])
        mock_create.assert_called_once()
    
    @patch('openai.embeddings.create')
    def test_recipe_embedding_generation(self, mock_create):
        """Test complete recipe embedding generation."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = [0.1] * 1536  # Standard embedding dimension
        mock_create.return_value = mock_response
        
        generator = RecipeEmbeddingGenerator()
        result = generator.generate_recipe_embedding(self.sample_recipe)
        
        # Check result structure
        self.assertIn('embedding', result)
        self.assertIn('text', result)
        self.assertIn('metadata', result)
        self.assertIn('recipe', result)
        
        # Check embedding
        self.assertEqual(len(result['embedding']), 1536)
        
        # Check metadata
        metadata = result['metadata']
        self.assertEqual(metadata['title'], "Test Chicken Rice")
        self.assertEqual(metadata['difficulty'], "Beginner")
        self.assertEqual(metadata['prep_time'], 15)
        self.assertEqual(metadata['cook_time'], 25)
        self.assertEqual(metadata['total_time'], 40)
        self.assertEqual(metadata['servings'], 4)
        self.assertEqual(metadata['ingredient_count'], 3)
        self.assertEqual(metadata['instruction_count'], 3)
    
    @patch('openai.embeddings.create')
    def test_batch_embedding_generation(self, mock_create):
        """Test batch embedding generation."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = [0.1] * 1536
        mock_create.return_value = mock_response
        
        # Create multiple recipes
        recipes = [
            self.sample_recipe,
            Recipe(
                title="Test Pasta",
                prep_time=10,
                cook_time=15,
                servings=2,
                difficulty="Intermediate",
                ingredients=["pasta", "tomato sauce"],
                instructions=["Cook pasta in boiling water", "Heat the sauce", "Add sauce to pasta"]
            )
        ]
        
        generator = RecipeEmbeddingGenerator()
        results = generator.generate_batch_embeddings(recipes)
        
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn('embedding', result)
            self.assertIn('metadata', result)
    

class TestVectorRecipeStore(unittest.TestCase):
    """Test vector store operations with mocked Chroma DB."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_recipe = Recipe(
            title="Test Recipe",
            prep_time=10,
            cook_time=20,
            servings=4,
            difficulty="Beginner",
            ingredients=["ingredient1", "ingredient2"],
            instructions=["first step", "second step", "third step"]
        )
        
    @patch('chromadb.HttpClient')
    @patch('src.vector_embeddings.RecipeEmbeddingGenerator')
    def test_store_initialization(self, mock_generator, mock_client):
        """Test vector store initialization."""
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        
        store = VectorRecipeStore()
        
        # Access client property to trigger initialization
        client = store.client
        
        mock_client.assert_called_once()
        mock_client_instance.heartbeat.assert_called_once()
    
    @patch('chromadb.HttpClient')
    @patch('src.vector_embeddings.RecipeEmbeddingGenerator')
    def test_add_single_recipe(self, mock_generator, mock_client):
        """Test adding a single recipe to vector store."""
        # Mock Chroma client
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        # Mock embedding generator
        mock_gen_instance = Mock()
        mock_generator.return_value = mock_gen_instance
        mock_gen_instance.generate_recipe_embedding.return_value = {
            'embedding': [0.1] * 1536,
            'text': 'test text',
            'metadata': {'title': 'Test Recipe'}
        }
        
        store = VectorRecipeStore()
        recipe_id = store.add_recipe(self.sample_recipe, "test_id")
        
        self.assertEqual(recipe_id, "test_id")
        mock_collection.add.assert_called_once()
    
    @patch('chromadb.HttpClient')
    @patch('src.vector_embeddings.RecipeEmbeddingGenerator')
    def test_search_recipes(self, mock_generator, mock_client):
        """Test recipe search functionality."""
        # Mock Chroma client and collection
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        # Mock search results
        mock_collection.query.return_value = {
            'ids': [['recipe1', 'recipe2']],
            'distances': [[0.1, 0.3]],
            'metadatas': [[{'title': 'Recipe 1'}, {'title': 'Recipe 2'}]],
            'documents': [['doc1', 'doc2']]
        }
        
        # Mock embedding generation for search
        mock_gen_instance = Mock()
        mock_generator.return_value = mock_gen_instance
        
        with patch('src.vector_store.create_search_embedding', return_value=[0.1] * 1536):
            store = VectorRecipeStore()
            results = store.search_recipes("test query")
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['id'], 'recipe1')
        self.assertEqual(results[0]['similarity'], 0.9)  # 1 - 0.1
        self.assertEqual(results[1]['similarity'], 0.7)  # 1 - 0.3
    
    @patch('chromadb.HttpClient')
    @patch('src.vector_embeddings.RecipeEmbeddingGenerator')
    def test_get_recipe_by_id(self, mock_generator, mock_client):
        """Test retrieving recipe by ID."""
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        # Mock get results
        mock_collection.get.return_value = {
            'ids': ['recipe1'],
            'metadatas': [{'title': 'Test Recipe'}],
            'documents': ['test document']
        }
        
        store = VectorRecipeStore()
        result = store.get_recipe_by_id("recipe1")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 'recipe1')
        self.assertEqual(result['metadata']['title'], 'Test Recipe')
    
    @patch('chromadb.HttpClient')
    @patch('src.vector_embeddings.RecipeEmbeddingGenerator')
    def test_count_recipes(self, mock_generator, mock_client):
        """Test counting recipes in store."""
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        mock_collection.count.return_value = 42
        
        store = VectorRecipeStore()
        count = store.count_recipes()
        
        self.assertEqual(count, 42)
    
    @patch('chromadb.HttpClient')
    @patch('src.vector_embeddings.RecipeEmbeddingGenerator')
    def test_update_recipe(self, mock_generator, mock_client):
        """Test recipe update functionality."""
        # Mock Chroma client and collection
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        # Mock embedding generation
        mock_gen_instance = Mock()
        mock_generator.return_value = mock_gen_instance
        mock_gen_instance.generate_recipe_embedding.return_value = {
            'embedding': [0.1, 0.2, 0.3],
            'text': 'Updated recipe text',
            'metadata': {'title': 'Updated Recipe', 'difficulty': 'Intermediate'}
        }
        
        # Create updated recipe
        updated_recipe = Recipe(
            title="Updated Chicken Rice",
            prep_time=20,
            cook_time=25,
            total_time=45,
            servings=6,
            difficulty="Intermediate",
            ingredients=["2 cups rice", "1 lb chicken", "Updated seasonings"],
            instructions=["Updated step 1", "Updated step 2", "Updated step 3"]
        )
        
        store = VectorRecipeStore()
        result = store.update_recipe("recipe_123", updated_recipe)
        
        # Verify update was successful
        self.assertTrue(result)
        
        # Verify update was called once with correct recipe ID
        mock_collection.update.assert_called_once()
        call_args = mock_collection.update.call_args
        
        # Verify the call included the correct ID
        self.assertEqual(call_args.kwargs['ids'], ["recipe_123"])
        
        # Verify embeddings, documents, and metadatas were provided
        self.assertIn('embeddings', call_args.kwargs)
        self.assertIn('documents', call_args.kwargs)
        self.assertIn('metadatas', call_args.kwargs)
        
        # Verify the metadata contains the updated recipe information
        metadata = call_args.kwargs['metadatas'][0]
        self.assertEqual(metadata['title'], 'Updated Chicken Rice')
        self.assertEqual(metadata['difficulty'], 'Intermediate')
        self.assertEqual(metadata['prep_time'], 20)
        self.assertEqual(metadata['cook_time'], 25)

class TestRecipeIngestionPipeline(unittest.TestCase):
    """Test recipe ingestion pipeline."""
    
    def test_pipeline_initialization(self):
        """Test that pipeline initializes correctly."""
        pipeline = RecipeIngestionPipeline()
        self.assertIsNotNone(pipeline.vector_store)
        self.assertEqual(pipeline.stats['processed'], 0)
        self.assertEqual(pipeline.stats['successful'], 0)
        self.assertEqual(pipeline.stats['failed'], 0)
    
    def test_recipe_id_generation(self):
        """Test recipe ID generation from titles."""
        pipeline = RecipeIngestionPipeline()
        recipe = Recipe(
            title="Chicken & Rice Bowl",
            prep_time=10, cook_time=20, servings=4, difficulty="Beginner",
            ingredients=["ing1", "ing2"], instructions=["step1", "step2", "step3"]
        )
        
        recipe_id = pipeline._generate_recipe_id(recipe)
        self.assertEqual(recipe_id, "recipe_chicken__rice_bowl")  # Special chars converted to underscores

class TestIntegration(unittest.TestCase):
    """Integration tests for vector operations."""
    
    @patch('openai.embeddings.create')
    @patch('chromadb.HttpClient')
    def test_end_to_end_workflow(self, mock_client, mock_openai):
        """Test complete workflow from embedding to search."""
        # Mock OpenAI
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = [0.1] * 1536
        mock_openai.return_value = mock_response
        
        # Mock Chroma
        mock_client_instance = Mock()
        mock_collection = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.heartbeat.return_value = True
        mock_client_instance.get_collection.return_value = mock_collection
        
        # Mock search results
        mock_collection.query.return_value = {
            'ids': [['recipe1']],
            'distances': [[0.2]],
            'metadatas': [[{'title': 'Found Recipe'}]],
            'documents': [['found document']]
        }
        
        recipe = Recipe(
            title="Test Recipe",
            prep_time=10, cook_time=20, servings=4, difficulty="Beginner",
            ingredients=["ingredient1", "ingredient2"], instructions=["instruction1", "instruction2", "instruction3"]
        )
        
        # Test workflow
        store = VectorRecipeStore()
        recipe_id = store.add_recipe(recipe)
        
        with patch('src.vector_store.create_search_embedding', return_value=[0.1] * 1536):
            results = store.search_recipes("test query")
        
        self.assertIsNotNone(recipe_id)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['metadata']['title'], 'Found Recipe')

if __name__ == '__main__':
    unittest.main()