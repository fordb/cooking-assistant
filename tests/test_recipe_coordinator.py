"""
Tests for simplified recipe coordinator.
"""

import pytest
from unittest.mock import Mock, patch

from src.core.recipe_coordinator import RecipeCoordinator, RecipeResult, process_recipe_input
from src.core.recipe_intent_classifier import RecipeIntent
from src.core.recipe_extractor import RecipeExtractionResult
from src.recipes.models import Recipe


class TestRecipeCoordinator:
    """Test simplified RecipeCoordinator."""
    
    def setup_method(self):
        """Reset singletons."""
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
    def test_recipe_creation_success(self, mock_classify, mock_extract):
        """Test successful recipe creation."""
        mock_classify.return_value = (RecipeIntent.REGULAR_COOKING, 0.95, "Recipe creation")
        
        test_recipe = Recipe(
            title="Test Recipe",
            ingredients=["ingredient 1", "ingredient 2"],
            instructions=["step 1", "step 2", "step 3"],
            prep_time=5, cook_time=10, servings=2, difficulty="Beginner"
        )
        
        mock_extract.return_value = RecipeExtractionResult(success=True, recipe=test_recipe)
        
        coordinator = RecipeCoordinator()
        result = coordinator.process("Make pasta with sauce")
        
        assert result.success is True
        assert result.intent == RecipeIntent.REGULAR_COOKING
        assert result.user is not None
        assert result.recipe.title == "Test Recipe"
        assert "Created recipe" in result.message
        assert result.user.recipe_count == 1
    
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_other_intents(self, mock_classify):
        """Test handling of other intents."""
        mock_classify.return_value = (RecipeIntent.FIND_RECIPES, 0.90, "Search")
        
        coordinator = RecipeCoordinator()
        result = coordinator.process("Find chicken recipes")
        
        assert result.success is True
        assert result.intent == RecipeIntent.FIND_RECIPES
        assert result.user is not None
        assert "not yet implemented" in result.message
    
    @patch('src.core.recipe_coordinator.extract_recipe_from_text')
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_extraction_failure(self, mock_classify, mock_extract):
        """Test extraction failure handling."""
        mock_classify.return_value = (RecipeIntent.REGULAR_COOKING, 0.90, "Recipe")
        mock_extract.return_value = RecipeExtractionResult(success=False, error="Failed")
        
        coordinator = RecipeCoordinator()
        result = coordinator.process("Make food")
        
        assert result.success is False
        assert result.intent == RecipeIntent.REGULAR_COOKING
        assert "Could not extract recipe" in result.message
    
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_exception_handling(self, mock_classify):
        """Test exception handling."""
        mock_classify.side_effect = Exception("Test error")
        
        coordinator = RecipeCoordinator()
        result = coordinator.process("Test input")
        
        assert result.success is False
        assert "Error: Test error" in result.message
    
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_convenience_function(self, mock_classify):
        """Test convenience function."""
        mock_classify.return_value = (RecipeIntent.LIST_RECIPES, 0.85, "List")
        
        result = process_recipe_input("List my recipes")
        
        assert result.success is True
        assert result.intent == RecipeIntent.LIST_RECIPES