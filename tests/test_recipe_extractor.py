"""
Tests for LLM-based recipe extraction system.
"""

import pytest
from unittest.mock import Mock, patch
import json

from src.core.recipe_extractor import (
    RecipeExtractor, RecipeExtractionResult, 
    get_recipe_extractor, extract_recipe_from_text
)


class TestRecipeExtractor:
    """Test RecipeExtractor class."""
    
    @patch('src.core.recipe_extractor.OpenAI')
    def test_extract_recipe_success(self, mock_openai_class):
        """Test successful LLM-based recipe extraction."""
        # Mock the OpenAI response structure
        mock_choice = Mock()
        mock_choice.message.content = json.dumps({
            "title": "Simple Pasta Recipe",
            "ingredients": ["1 lb pasta", "2 cups tomato sauce", "1/2 cup parmesan cheese"],
            "instructions": [
                "Cook pasta in boiling water for 10 minutes",
                "Heat tomato sauce in a pan", 
                "Mix pasta with sauce and serve with cheese"
            ],
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
        
        text = "Simple pasta with tomato sauce and cheese"
        result = extractor.extract_recipe(text)
        
        assert result.success is True
        assert result.recipe is not None
        
        recipe = result.recipe
        assert recipe.title == "Simple Pasta Recipe"
        assert len(recipe.ingredients) == 3
        assert len(recipe.instructions) == 3
        assert recipe.prep_time == 5
        assert recipe.cook_time == 15
        assert recipe.servings == 4
        
        # Verify LLM was called with proper prompt
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert "Extract recipe information" in call_args[1]['messages'][0]['content']
    
    @patch('src.core.recipe_extractor.OpenAI')
    def test_extract_recipe_with_override_name(self, mock_openai_class):
        """Test extraction with name override."""
        mock_choice = Mock()
        mock_choice.message.content = json.dumps({
            "title": "Custom Recipe Name",
            "ingredients": ["2 cups flour", "1 cup sugar"],
            "instructions": ["Mix ingredients", "Bake for 30 minutes", "Cool before serving"],
            "prep_time": 10,
            "cook_time": 30,
            "servings": 8
        })
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        extractor = RecipeExtractor()
        
        result = extractor.extract_recipe("Some recipe text", recipe_name="Custom Recipe Name")
        
        assert result.success is True
        assert result.recipe.title == "Custom Recipe Name"
        
        # Verify prompt included the custom name
        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]['messages'][0]['content']
        assert 'Use "Custom Recipe Name" as the title' in prompt
    
    @patch('src.core.recipe_extractor.OpenAI')
    def test_extract_recipe_malformed_json(self, mock_openai_class):
        """Test handling of malformed JSON response."""
        mock_choice = Mock()
        mock_choice.message.content = "This is not valid JSON"
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        extractor = RecipeExtractor()
        
        result = extractor.extract_recipe("Some text")
        
        # Should still succeed with fallback data
        assert result.success is True
        assert result.recipe.title == "Extracted Recipe"
        assert len(result.recipe.ingredients) >= 2
        assert len(result.recipe.instructions) >= 3
    
    @patch('src.core.recipe_extractor.OpenAI')
    def test_parse_json_with_code_blocks(self, mock_openai_class):
        """Test JSON parsing with code block formatting."""
        mock_choice = Mock()
        mock_choice.message.content = '''```json
        {
            "title": "Test Recipe",
            "ingredients": ["ingredient 1", "ingredient 2"],
            "instructions": ["step 1", "step 2", "step 3"],
            "prep_time": 5,
            "cook_time": 10,
            "servings": 2
        }
        ```'''
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        extractor = RecipeExtractor()
        
        result = extractor.extract_recipe("Test recipe text")
        
        assert result.success is True
        assert result.recipe.title == "Test Recipe"
        assert len(result.recipe.ingredients) == 2
        assert len(result.recipe.instructions) == 3
    
    def test_build_extraction_prompt(self):
        """Test prompt building logic."""
        with patch('src.core.recipe_extractor.OpenAI'):
            extractor = RecipeExtractor()
        
        # Test without custom name
        prompt = extractor._build_extraction_prompt("Test recipe text")
        assert "Extract recipe information" in prompt
        assert "Test recipe text" in prompt
        assert "Required JSON format" in prompt
        
        # Test with custom name
        prompt_with_name = extractor._build_extraction_prompt("Test text", "Custom Name")
        assert 'Use "Custom Name" as the title' in prompt_with_name
    
    def test_parse_json_response_fallback(self):
        """Test JSON parsing fallback behavior."""
        with patch('src.core.recipe_extractor.OpenAI'):
            extractor = RecipeExtractor()
        
        # Test with invalid JSON
        result = extractor._parse_json_response("invalid json")
        
        assert result["title"] == "Extracted Recipe"
        assert len(result["ingredients"]) == 2
        assert len(result["instructions"]) == 3
        assert result["prep_time"] == 10


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def setup_method(self):
        """Reset singleton for clean tests."""
        import src.core.recipe_extractor
        src.core.recipe_extractor._extractor = None
    
    @patch('src.core.recipe_extractor.OpenAI')
    def test_extract_recipe_from_text_convenience(self, mock_openai_class):
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
        
        result = extract_recipe_from_text("Test recipe text")
        
        assert result.success is True
        assert result.recipe.title == "Simple Recipe"
    
    def test_singleton_pattern(self):
        """Test singleton pattern works."""
        with patch('src.core.recipe_extractor.OpenAI'):
            extractor1 = get_recipe_extractor()
            extractor2 = get_recipe_extractor()
            assert extractor1 is extractor2