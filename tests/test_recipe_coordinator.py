"""
Tests for recipe management coordinator.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from src.core.recipe_coordinator import (
    RecipeCoordinator, CoordinationResult, CoordinationStatus, 
    get_recipe_coordinator, process_recipe_input
)
from src.core.recipe_intent_classifier import RecipeIntent
from src.core.user_identity import UserProfile
from src.core.recipe_extractor import RecipeExtractionResult
from src.recipes.models import Recipe


class TestRecipeCoordinator:
    """Test RecipeCoordinator class."""
    
    def setup_method(self):
        """Setup for each test."""
        # Reset singleton
        import src.core.recipe_coordinator
        src.core.recipe_coordinator._coordinator = None
        
        # Reset other singletons
        import src.core.recipe_intent_classifier
        src.core.recipe_intent_classifier._classifier_instance = None
        
        import src.core.user_identity
        src.core.user_identity._identity_manager = None
        
        import src.core.recipe_extractor
        src.core.recipe_extractor._extractor = None
    
    @patch('src.core.recipe_coordinator.extract_recipe_from_text')
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_process_recipe_creation_success(self, mock_classify, mock_extract):
        """Test successful recipe creation flow."""
        # Mock intent classification
        mock_classify.return_value = (RecipeIntent.REGULAR_COOKING, 0.95, "Recipe creation request")
        
        # Mock recipe extraction
        test_recipe = Recipe(
            title="Test Recipe",
            ingredients=["ingredient 1", "ingredient 2"],
            instructions=["step 1", "step 2", "step 3"],
            prep_time=5,
            cook_time=10,
            servings=2,
            difficulty="Beginner"
        )
        
        mock_extract.return_value = RecipeExtractionResult(
            success=True,
            recipe=test_recipe
        )
        
        coordinator = RecipeCoordinator()
        result = coordinator.process_user_input("I want to make pasta with sauce")
        
        assert result.status == CoordinationStatus.SUCCESS
        assert result.intent == RecipeIntent.REGULAR_COOKING
        assert result.user is not None
        assert result.recipe is not None
        assert result.recipe.title == "Test Recipe"
        assert "Successfully created recipe" in result.message
        
        # Verify user recipe count was incremented
        assert result.user.recipe_count == 1
    
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_process_recipe_search_request(self, mock_classify):
        """Test recipe search request handling."""
        mock_classify.return_value = (RecipeIntent.FIND_RECIPES, 0.90, "Search request")
        
        coordinator = RecipeCoordinator()
        result = coordinator.process_user_input("Find me a chicken recipe")
        
        assert result.status == CoordinationStatus.PARTIAL
        assert result.intent == RecipeIntent.FIND_RECIPES
        assert result.user is not None
        assert "Recipe search functionality" in result.message
    
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_process_with_existing_session(self, mock_classify):
        """Test processing with existing session."""
        mock_classify.return_value = (RecipeIntent.LIST_RECIPES, 0.85, "List request")
        
        coordinator = RecipeCoordinator()
        
        # First request creates user
        result1 = coordinator.process_user_input("List my recipes")
        user_id = result1.user.user_id
        
        # Create a session for the user
        session_id = coordinator.identity_manager.create_session(user_id)
        
        # Second request with session should use same user
        result2 = coordinator.process_user_input("Show my recipes again", session_id)
        
        assert result2.user.user_id == user_id
        assert result2.status == CoordinationStatus.PARTIAL
        assert result2.intent == RecipeIntent.LIST_RECIPES
    
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_process_intent_classification_failure(self, mock_classify):
        """Test handling of intent classification failure."""
        mock_classify.side_effect = Exception("Classification failed")
        
        coordinator = RecipeCoordinator()
        result = coordinator.process_user_input("Some unclear text")
        
        assert result.status == CoordinationStatus.FAILED
        assert "Coordination failed" in result.error
    
    @patch('src.core.recipe_coordinator.extract_recipe_from_text')
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_process_recipe_extraction_failure(self, mock_classify, mock_extract):
        """Test handling of recipe extraction failure."""
        mock_classify.return_value = (RecipeIntent.REGULAR_COOKING, 0.90, "Recipe creation")
        
        mock_extract.return_value = RecipeExtractionResult(
            success=False,
            error="Extraction failed"
        )
        
        coordinator = RecipeCoordinator()
        result = coordinator.process_user_input("Make some food")
        
        assert result.status == CoordinationStatus.FAILED
        assert result.intent == RecipeIntent.REGULAR_COOKING
        assert "Failed to extract recipe" in result.error
    
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_process_save_recipe_request(self, mock_classify):
        """Test recipe save request handling."""
        mock_classify.return_value = (RecipeIntent.SAVE_RECIPE, 0.95, "Save request")
        
        coordinator = RecipeCoordinator()
        result = coordinator.process_user_input("Save this recipe")
        
        assert result.status == CoordinationStatus.PARTIAL
        assert result.intent == RecipeIntent.SAVE_RECIPE
        assert "Recipe save functionality" in result.message
    
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_process_delete_recipe_request(self, mock_classify):
        """Test recipe deletion request handling."""
        mock_classify.return_value = (RecipeIntent.DELETE_RECIPE, 0.88, "Delete request")
        
        coordinator = RecipeCoordinator()
        result = coordinator.process_user_input("Delete my pasta recipe")
        
        assert result.status == CoordinationStatus.PARTIAL
        assert result.intent == RecipeIntent.DELETE_RECIPE
        assert "Recipe deletion functionality" in result.message
    
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_process_exception_handling(self, mock_classify):
        """Test exception handling in process_user_input."""
        mock_classify.side_effect = Exception("Test exception")
        
        coordinator = RecipeCoordinator()
        result = coordinator.process_user_input("Test input")
        
        assert result.status == CoordinationStatus.FAILED
        assert "Coordination failed" in result.error
        assert "Test exception" in result.error


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def setup_method(self):
        """Reset singletons for clean tests."""
        import src.core.recipe_coordinator
        src.core.recipe_coordinator._coordinator = None
        
        import src.core.recipe_intent_classifier
        src.core.recipe_intent_classifier._classifier_instance = None
        
        import src.core.user_identity
        src.core.user_identity._identity_manager = None
    
    def test_singleton_pattern(self):
        """Test singleton pattern works."""
        coordinator1 = get_recipe_coordinator()
        coordinator2 = get_recipe_coordinator()
        assert coordinator1 is coordinator2
    
    @patch('src.core.recipe_coordinator.classify_recipe_intent')
    def test_process_recipe_input_convenience(self, mock_classify):
        """Test convenience function."""
        mock_classify.return_value = (RecipeIntent.REGULAR_COOKING, 0.80, "General cooking")
        
        result = process_recipe_input("Test input")
        
        assert result.status == CoordinationStatus.SUCCESS
        assert result.intent == RecipeIntent.REGULAR_COOKING
        assert result.user is not None