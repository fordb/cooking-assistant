"""
Test CookingAssistant integration with recipe management.
"""

import pytest
from unittest.mock import patch, Mock
import json

from src.core.cooking_assistant import CookingAssistant, manage_recipe
from src.core.recipe_intent_classifier import RecipeIntent
from src.recipes.models import Recipe


class TestCookingAssistantIntegration:
    """Test CookingAssistant integration with recipe management."""
    
    def setup_method(self):
        """Reset singletons for clean tests."""
        import src.core.recipe_coordinator
        src.core.recipe_coordinator._coordinator = None
        
        import src.core.recipe_intent_classifier
        src.core.recipe_intent_classifier._classifier_instance = None
        
        import src.core.user_identity
        src.core.user_identity._identity_manager = None
        
        import src.core.recipe_extractor
        src.core.recipe_extractor._extractor = None
    
    @patch('src.core.recipe_coordinator.extract_recipe_from_text')
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_manage_recipe_creation(self, mock_classify, mock_extract):
        """Test recipe creation through CookingAssistant."""
        # Setup mocks
        mock_classify.return_value = (RecipeIntent.REGULAR_COOKING, 0.95, "Recipe creation")
        
        test_recipe = Recipe(
            title="Simple Pasta",
            ingredients=["pasta", "tomato sauce"],
            instructions=["Cook pasta", "Add sauce", "Serve"],
            prep_time=5,
            cook_time=10,
            servings=2,
            difficulty="Beginner"
        )
        
        mock_extract.return_value = Mock(success=True, recipe=test_recipe)
        
        # Test integration
        assistant = CookingAssistant()
        result = assistant.manage_recipe("I want to make pasta with tomato sauce")
        
        assert result['success'] is True
        assert result['intent'] == 'regular_cooking'
        assert result['recipe']['title'] == 'Simple Pasta'
        assert result['recipe']['ingredients'] == ['pasta', 'tomato sauce']
        assert result['user_recipe_count'] == 1
        assert 'Created recipe' in result['message']
    
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_manage_recipe_search(self, mock_classify):
        """Test recipe search through CookingAssistant."""
        mock_classify.return_value = (RecipeIntent.FIND_RECIPES, 0.90, "Search request")
        
        assistant = CookingAssistant()
        result = assistant.manage_recipe("Find my chicken recipes")
        
        assert result['success'] is True
        assert result['intent'] == 'find_recipes'
        assert 'not yet implemented' in result['message']
        assert result['recipe'] is None
        assert result['user_recipe_count'] >= 0
    
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_session_persistence(self, mock_classify):
        """Test that session persists across recipe management calls."""
        mock_classify.return_value = (RecipeIntent.LIST_RECIPES, 0.85, "List request")
        
        assistant = CookingAssistant()
        
        # First call should create session
        result1 = assistant.manage_recipe("List my recipes")
        session_id = assistant._session_id
        
        assert session_id is not None
        assert result1['success'] is True
        
        # Second call should use same session
        result2 = assistant.manage_recipe("Show my recipes again")
        assert assistant._session_id == session_id
        assert result2['success'] is True
    
    @patch('src.core.cooking_assistant.process_recipe_input')
    def test_manage_recipe_error_handling(self, mock_process):
        """Test error handling in recipe management."""
        mock_process.return_value = Mock(
            success=False,
            message="Error occurred",
            intent=None,
            recipe=None,
            user=None
        )
        
        assistant = CookingAssistant()
        result = assistant.manage_recipe("Invalid input")
        
        assert result['success'] is False
        assert result['message'] == "Error occurred"
        assert result['intent'] is None
        assert result['recipe'] is None
        assert result['user_recipe_count'] == 0
    
    @patch('src.core.cooking_assistant.process_recipe_input')
    def test_convenience_function(self, mock_process):
        """Test convenience function for recipe management."""
        mock_process.return_value = Mock(
            success=True,
            message="Recipe saved",
            intent=RecipeIntent.SAVE_RECIPE,
            recipe=None,
            user=Mock(recipe_count=5)
        )
        
        result = manage_recipe("Save my pasta recipe")
        
        assert result['success'] is True
        assert result['message'] == "Recipe saved"
        assert result['intent'] == 'save_recipe'
        assert result['user_recipe_count'] == 5