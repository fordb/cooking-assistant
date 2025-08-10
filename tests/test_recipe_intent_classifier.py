"""
Comprehensive test suite for recipe intent classification.
Tests LLM-based flexible intent detection with 30+ diverse scenarios.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from src.core.recipe_intent_classifier import (
    RecipeIntentClassifier, 
    RecipeIntent,
    classify_recipe_intent,
    RecipeIntentClassificationError
)


class TestRecipeIntentClassifier:
    """Test suite for LLM-based recipe intent classification."""
    
    @pytest.fixture
    def mock_openai_response(self):
        """Create mock OpenAI response."""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Intent: SAVE_RECIPE\nConfidence: 0.95\nReasoning: Clear request to save a recipe"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        return mock_response

    @pytest.fixture
    def classifier(self, mock_openai_response):
        """Create classifier with mocked OpenAI client."""
        with patch('src.core.recipe_intent_classifier.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_openai_response
            mock_openai.return_value = mock_client
            
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
                return RecipeIntentClassifier()

    def test_classifier_initialization_success(self):
        """Test successful classifier initialization with API key."""
        with patch('src.core.recipe_intent_classifier.OpenAI') as mock_openai:
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
                classifier = RecipeIntentClassifier()
                mock_openai.assert_called_once_with(api_key='test-key')

    def test_classifier_initialization_no_api_key(self):
        """Test classifier initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RecipeIntentClassificationError, match="OpenAI API key not found"):
                RecipeIntentClassifier()

    # SAVE_RECIPE Intent Tests
    @pytest.mark.parametrize("query,expected_intent", [
        ("Save this recipe", RecipeIntent.SAVE_RECIPE),
        ("save this recipe to my collection", RecipeIntent.SAVE_RECIPE),
        ("Remember this one for me", RecipeIntent.SAVE_RECIPE),
        ("I want to keep this recipe", RecipeIntent.SAVE_RECIPE),
        ("Add this to my recipe book", RecipeIntent.SAVE_RECIPE),
        ("Store this for later", RecipeIntent.SAVE_RECIPE),
        ("Can you save this recipe?", RecipeIntent.SAVE_RECIPE),
        ("I'd like to add this to my collection", RecipeIntent.SAVE_RECIPE),
        ("Please remember this recipe", RecipeIntent.SAVE_RECIPE),
    ])
    def test_save_recipe_intents(self, classifier, query, expected_intent):
        """Test various save recipe intent variations."""
        # Mock different responses for save intents
        with patch.object(classifier.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = f"Intent: {expected_intent.value.upper()}\nConfidence: 0.92\nReasoning: Request to save recipe"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response
            
            intent, confidence, reasoning = classifier.classify_intent(query)
            assert intent == expected_intent
            assert confidence > 0.8
            assert "save" in reasoning.lower() or "store" in reasoning.lower() or "remember" in reasoning.lower()

    # FIND_RECIPES Intent Tests
    @pytest.mark.parametrize("query,expected_intent", [
        ("Show me my pasta recipes", RecipeIntent.FIND_RECIPES),
        ("Find my chicken dishes", RecipeIntent.FIND_RECIPES),
        ("What Italian recipes do I have?", RecipeIntent.FIND_RECIPES),
        ("Search for my quick meals", RecipeIntent.FIND_RECIPES),
        ("I'm looking for my vegetarian recipes", RecipeIntent.FIND_RECIPES),
        ("Do I have any soup recipes saved?", RecipeIntent.FIND_RECIPES),
        ("Show me recipes with beef", RecipeIntent.FIND_RECIPES),
        ("What recipes can I make in 30 minutes?", RecipeIntent.FIND_RECIPES),
        ("Find my dessert recipes", RecipeIntent.FIND_RECIPES),
    ])
    def test_find_recipes_intents(self, classifier, query, expected_intent):
        """Test various find recipes intent variations."""
        with patch.object(classifier.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = f"Intent: {expected_intent.value.upper()}\nConfidence: 0.90\nReasoning: Search for specific recipes"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response
            
            intent, confidence, reasoning = classifier.classify_intent(query)
            assert intent == expected_intent
            assert confidence > 0.8

    # LIST_RECIPES Intent Tests
    @pytest.mark.parametrize("query,expected_intent", [
        ("What recipes do I have?", RecipeIntent.LIST_RECIPES),
        ("Show me all my recipes", RecipeIntent.LIST_RECIPES),
        ("List my recipe collection", RecipeIntent.LIST_RECIPES),
        ("What's in my recipe book?", RecipeIntent.LIST_RECIPES),
        ("Show me everything I've saved", RecipeIntent.LIST_RECIPES),
        ("Display my recipe collection", RecipeIntent.LIST_RECIPES),
    ])
    def test_list_recipes_intents(self, classifier, query, expected_intent):
        """Test various list recipes intent variations."""
        with patch.object(classifier.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = f"Intent: {expected_intent.value.upper()}\nConfidence: 0.93\nReasoning: Request to list all recipes"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response
            
            intent, confidence, reasoning = classifier.classify_intent(query)
            assert intent == expected_intent
            assert confidence > 0.8

    # DELETE_RECIPE Intent Tests
    @pytest.mark.parametrize("query,expected_intent", [
        ("Delete the pasta recipe", RecipeIntent.DELETE_RECIPE),
        ("Remove this recipe from my collection", RecipeIntent.DELETE_RECIPE),
        ("I don't want this recipe anymore", RecipeIntent.DELETE_RECIPE),
        ("Can you delete the chicken recipe?", RecipeIntent.DELETE_RECIPE),
        ("Remove this from my saved recipes", RecipeIntent.DELETE_RECIPE),
        ("Get rid of this recipe", RecipeIntent.DELETE_RECIPE),
    ])
    def test_delete_recipe_intents(self, classifier, query, expected_intent):
        """Test various delete recipe intent variations."""
        with patch.object(classifier.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = f"Intent: {expected_intent.value.upper()}\nConfidence: 0.88\nReasoning: Request to remove recipe"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response
            
            intent, confidence, reasoning = classifier.classify_intent(query)
            assert intent == expected_intent
            assert confidence > 0.8

    # REGULAR_COOKING Intent Tests
    @pytest.mark.parametrize("query,expected_intent", [
        ("How do I make carbonara?", RecipeIntent.REGULAR_COOKING),
        ("What temperature should I cook chicken?", RecipeIntent.REGULAR_COOKING),
        ("Can you suggest a quick dinner?", RecipeIntent.REGULAR_COOKING),
        ("I need a recipe for chocolate cake", RecipeIntent.REGULAR_COOKING),
        ("How long do I cook pasta?", RecipeIntent.REGULAR_COOKING),
        ("What spices go well with lamb?", RecipeIntent.REGULAR_COOKING),
        ("Can you help me with a vegetarian meal?", RecipeIntent.REGULAR_COOKING),
        ("I have chicken and rice, what can I make?", RecipeIntent.REGULAR_COOKING),
    ])
    def test_regular_cooking_intents(self, classifier, query, expected_intent):
        """Test various regular cooking intent variations."""
        with patch.object(classifier.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = f"Intent: {expected_intent.value.upper()}\nConfidence: 0.94\nReasoning: General cooking question"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response
            
            intent, confidence, reasoning = classifier.classify_intent(query)
            assert intent == expected_intent
            assert confidence > 0.8

    # Edge Cases and Ambiguous Queries
    def test_ambiguous_queries(self, classifier):
        """Test handling of ambiguous queries."""
        ambiguous_queries = [
            "recipe",  # Very short, unclear
            "what about pasta?",  # Vague reference
            "that one",  # Unclear reference
            "yes",  # Single word response
            "can you help?",  # Generic request
        ]
        
        for query in ambiguous_queries:
            with patch.object(classifier.client.chat.completions, 'create') as mock_create:
                mock_response = Mock()
                mock_choice = Mock()
                mock_message = Mock()
                mock_message.content = "Intent: REGULAR_COOKING\nConfidence: 0.6\nReasoning: Ambiguous query, defaulting to regular cooking"
                mock_choice.message = mock_message
                mock_response.choices = [mock_choice]
                mock_create.return_value = mock_response
                
                intent, confidence, reasoning = classifier.classify_intent(query)
                # Ambiguous queries should have lower confidence
                assert confidence <= 0.8

    def test_context_aware_classification(self, classifier):
        """Test classification with conversation context."""
        query = "save this one"
        context = {"recent_recipes": ["pasta carbonara", "chicken parmesan"]}
        
        with patch.object(classifier.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = "Intent: SAVE_RECIPE\nConfidence: 0.92\nReasoning: Context indicates recipe to save"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response
            
            intent, confidence, reasoning = classifier.classify_intent(query, context)
            
            # Verify context was included in the prompt
            call_args = mock_create.call_args[1]
            prompt = call_args['messages'][0]['content']
            assert "pasta carbonara" in prompt
            assert intent == RecipeIntent.SAVE_RECIPE

    def test_classification_error_handling(self, classifier):
        """Test error handling during classification."""
        with patch.object(classifier.client.chat.completions, 'create') as mock_create:
            mock_create.side_effect = Exception("API Error")
            
            intent, confidence, reasoning = classifier.classify_intent("save this recipe")
            
            # Should fallback to regular cooking with explanation
            assert intent == RecipeIntent.REGULAR_COOKING
            assert confidence == 0.5
            assert "Classification failed" in reasoning

    def test_malformed_response_parsing(self, classifier):
        """Test parsing of malformed LLM responses."""
        with patch.object(classifier.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = "Malformed response without proper format"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response
            
            intent, confidence, reasoning = classifier.classify_intent("save this recipe")
            
            # Should fallback gracefully
            assert intent == RecipeIntent.REGULAR_COOKING
            assert confidence == 0.5

    def test_intent_enum_values(self, classifier):
        """Test intent enum values and direct comparisons."""
        # Test direct intent comparisons (replacing removed helper methods)
        recipe_management_intents = {RecipeIntent.SAVE_RECIPE, RecipeIntent.FIND_RECIPES, 
                                   RecipeIntent.LIST_RECIPES, RecipeIntent.DELETE_RECIPE}
        
        assert RecipeIntent.SAVE_RECIPE in recipe_management_intents
        assert RecipeIntent.FIND_RECIPES in recipe_management_intents
        assert RecipeIntent.REGULAR_COOKING not in recipe_management_intents
        
        # Test intents that require user recipes
        user_recipe_intents = {RecipeIntent.FIND_RECIPES, RecipeIntent.LIST_RECIPES, RecipeIntent.DELETE_RECIPE}
        
        assert RecipeIntent.FIND_RECIPES in user_recipe_intents
        assert RecipeIntent.LIST_RECIPES in user_recipe_intents
        assert RecipeIntent.DELETE_RECIPE in user_recipe_intents
        assert RecipeIntent.SAVE_RECIPE not in user_recipe_intents
        assert RecipeIntent.REGULAR_COOKING not in user_recipe_intents

    def test_convenience_function(self):
        """Test the convenience function for intent classification."""
        with patch('src.core.recipe_intent_classifier.RecipeIntentClassifier') as mock_classifier_class:
            mock_classifier = Mock()
            mock_classifier.classify_intent.return_value = (RecipeIntent.SAVE_RECIPE, 0.95, "Test reasoning")
            mock_classifier_class.return_value = mock_classifier
            
            intent, confidence, reasoning = classify_recipe_intent("save this recipe")
            
            assert intent == RecipeIntent.SAVE_RECIPE
            assert confidence == 0.95
            assert reasoning == "Test reasoning"
            mock_classifier.classify_intent.assert_called_once_with("save this recipe", None)


