"""
Tests for simplified recipe extraction.
"""

import pytest
from unittest.mock import Mock, patch
import json

from src.core.recipe_extractor import RecipeExtractor, RecipeExtractionResult, extract_recipe_from_text


class TestRecipeExtractor:
    """Test simplified RecipeExtractor."""
    
    def setup_method(self):
        """Reset singleton."""
        import src.core.recipe_extractor
        src.core.recipe_extractor._extractor = None
    
    @patch('src.core.recipe_extractor.OpenAI')
    def test_extract_recipe_success(self, mock_openai_class):
        """Test successful recipe extraction."""
        mock_choice = Mock()
        mock_choice.message.content = json.dumps({
            "title": "Test Recipe",
            "ingredients": ["1 cup flour", "2 eggs"],
            "instructions": ["Mix ingredients", "Cook", "Serve"],
            "prep_time": 5,
            "cook_time": 15,
            "servings": 4
        })
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        extractor = RecipeExtractor()
        result = extractor.extract_recipe("Make a simple recipe")
        
        assert result.success is True
        assert result.recipe is not None
        assert result.recipe.title == "Test Recipe"
        assert len(result.recipe.ingredients) == 2
        assert len(result.recipe.instructions) == 3
    
    @patch('src.core.recipe_extractor.OpenAI')
    def test_extract_recipe_with_name(self, mock_openai_class):
        """Test extraction with custom name."""
        mock_choice = Mock()
        mock_choice.message.content = json.dumps({
            "title": "Custom Recipe",
            "ingredients": ["ingredient 1", "ingredient 2"],
            "instructions": ["step 1", "step 2", "step 3"],
            "prep_time": 10,
            "cook_time": 20,
            "servings": 2
        })
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        extractor = RecipeExtractor()
        result = extractor.extract_recipe("Some text", recipe_name="Custom Recipe")
        
        assert result.success is True
        assert result.recipe.title == "Custom Recipe"
    
    @patch('src.core.recipe_extractor.OpenAI')
    def test_extract_recipe_malformed_json(self, mock_openai_class):
        """Test handling of malformed JSON."""
        mock_choice = Mock()
        mock_choice.message.content = "Not valid JSON"
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        extractor = RecipeExtractor()
        result = extractor.extract_recipe("Some text")
        
        # Should succeed with fallback
        assert result.success is True
        assert result.recipe.title == "Extracted Recipe"
    
    @patch('src.core.recipe_extractor.OpenAI')
    def test_convenience_function(self, mock_openai_class):
        """Test convenience function."""
        mock_choice = Mock()
        mock_choice.message.content = json.dumps({
            "title": "Simple Recipe",
            "ingredients": ["ingredient 1", "ingredient 2"],
            "instructions": ["step 1", "step 2", "step 3"],
            "prep_time": 5,
            "cook_time": 10,
            "servings": 2
        })
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        result = extract_recipe_from_text("Test recipe")
        
        assert result.success is True
        assert result.recipe.title == "Simple Recipe"