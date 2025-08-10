"""
LLM-based recipe intent classifier for conversational recipe management.
Uses flexible few-shot prompting to detect user intentions for recipe operations.
"""

from typing import Dict, Any, Tuple, Optional
from enum import Enum
import os
import json
from openai import OpenAI

from src.common.config import get_openai_config, get_logger
from src.common.exceptions import CookingAssistantError

logger = get_logger(__name__)


class RecipeIntent(Enum):
    """Recipe management intent categories."""
    SAVE_RECIPE = "save_recipe"
    FIND_RECIPES = "find_recipes" 
    LIST_RECIPES = "list_recipes"
    DELETE_RECIPE = "delete_recipe"
    REGULAR_COOKING = "regular_cooking"


class RecipeIntentClassificationError(CookingAssistantError):
    """Exception raised during recipe intent classification."""
    pass


class RecipeIntentClassifier:
    """
    LLM-based classifier for detecting recipe management intents in user queries.
    Uses few-shot prompting for flexible, robust intent detection.
    """
    
    def __init__(self):
        """Initialize the classifier with OpenAI client."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise RecipeIntentClassificationError("OpenAI API key not found")
        
        self.client = OpenAI(api_key=api_key)
        self.config = get_openai_config()
    
    def classify_intent(self, query: str, conversation_context: Optional[Dict] = None) -> Tuple[RecipeIntent, float, str]:
        """
        Classify the intent of a user query using LLM-based few-shot prompting.
        
        Args:
            query: User's query to classify
            conversation_context: Optional conversation context for better classification
            
        Returns:
            Tuple of (intent, confidence, reasoning)
        """
        try:
            prompt = self._build_classification_prompt(query, conversation_context)
            
            response = self.client.chat.completions.create(
                model=self.config.DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=150
            )
            
            result = response.choices[0].message.content.strip()
            return self._parse_classification_result(result)
            
        except Exception as e:
            logger.error(f"Failed to classify recipe intent for query '{query[:50]}...': {e}")
            # Fallback to regular cooking intent
            return RecipeIntent.REGULAR_COOKING, 0.5, f"Classification failed: {str(e)}"
    
    def _build_classification_prompt(self, query: str, context: Optional[Dict] = None) -> str:
        """Build few-shot classification prompt with diverse examples."""
        
        context_info = ""
        if context and context.get('recent_recipes'):
            context_info = f"\nRecent conversation context: User recently discussed/generated recipes about {context['recent_recipes']}"
        
        return f"""You are an expert at understanding user intentions for recipe management. Classify the following query into one of these categories:

SAVE_RECIPE: User wants to save, store, or remember a recipe
FIND_RECIPES: User wants to search for or retrieve specific recipes from their collection  
LIST_RECIPES: User wants to see all their recipes or browse their collection
DELETE_RECIPE: User wants to remove or delete a recipe from their collection
REGULAR_COOKING: Regular cooking questions, recipe generation, or cooking advice

Examples:

Query: "Save this recipe to my collection"
Intent: SAVE_RECIPE
Confidence: 0.95
Reasoning: Clear request to save a recipe

Query: "I want to keep this one for later"
Intent: SAVE_RECIPE  
Confidence: 0.90
Reasoning: Implicit request to store/remember a recipe

Query: "Show me my pasta recipes"
Intent: FIND_RECIPES
Confidence: 0.95
Reasoning: Specific search request for user's pasta recipes

Query: "What chicken dishes do I have saved?"
Intent: FIND_RECIPES
Confidence: 0.92
Reasoning: Query about specific recipes in user's collection

Query: "What recipes do I have?"
Intent: LIST_RECIPES
Confidence: 0.95
Reasoning: Request to see all saved recipes

Query: "Show me everything I've saved"
Intent: LIST_RECIPES
Confidence: 0.90
Reasoning: Request to browse entire recipe collection

Query: "Delete the lasagna recipe"
Intent: DELETE_RECIPE
Confidence: 0.95
Reasoning: Clear request to remove specific recipe

Query: "I don't want this recipe anymore"
Intent: DELETE_RECIPE
Confidence: 0.85
Reasoning: Request to remove a recipe, likely recently discussed

Query: "How do I make carbonara?"
Intent: REGULAR_COOKING
Confidence: 0.95
Reasoning: Request for recipe generation or cooking instruction

Query: "What temperature should I cook chicken at?"
Intent: REGULAR_COOKING
Confidence: 0.95
Reasoning: General cooking advice question

Query: "Can you suggest a quick dinner?"
Intent: REGULAR_COOKING
Confidence: 0.90
Reasoning: Request for recipe suggestions/generation{context_info}

Now classify this query:
Query: "{query}"

Respond in exactly this format:
Intent: [INTENT]
Confidence: [0.0-1.0]
Reasoning: [brief explanation]"""

    def _parse_classification_result(self, result: str) -> Tuple[RecipeIntent, float, str]:
        """Parse the LLM classification result."""
        try:
            lines = result.strip().split('\n')
            intent_str = None
            confidence = 0.5
            reasoning = "No reasoning provided"
            
            for line in lines:
                line = line.strip()
                if line.startswith('Intent:'):
                    intent_str = line.replace('Intent:', '').strip()
                elif line.startswith('Confidence:'):
                    try:
                        confidence = float(line.replace('Confidence:', '').strip())
                    except ValueError:
                        confidence = 0.5
                elif line.startswith('Reasoning:'):
                    reasoning = line.replace('Reasoning:', '').strip()
            
            # Map intent string to enum
            intent_mapping = {
                'SAVE_RECIPE': RecipeIntent.SAVE_RECIPE,
                'FIND_RECIPES': RecipeIntent.FIND_RECIPES,
                'LIST_RECIPES': RecipeIntent.LIST_RECIPES,
                'DELETE_RECIPE': RecipeIntent.DELETE_RECIPE,
                'REGULAR_COOKING': RecipeIntent.REGULAR_COOKING
            }
            
            intent = intent_mapping.get(intent_str, RecipeIntent.REGULAR_COOKING)
            
            return intent, confidence, reasoning
            
        except Exception as e:
            logger.error(f"Failed to parse classification result: {result}. Error: {e}")
            return RecipeIntent.REGULAR_COOKING, 0.5, f"Parse error: {str(e)}"
    
    def is_recipe_management_intent(self, intent: RecipeIntent) -> bool:
        """Check if the intent is related to recipe management (not regular cooking)."""
        return intent != RecipeIntent.REGULAR_COOKING
    
    def requires_user_recipes(self, intent: RecipeIntent) -> bool:
        """Check if the intent requires access to user's recipe collection."""
        return intent in [RecipeIntent.FIND_RECIPES, RecipeIntent.LIST_RECIPES, RecipeIntent.DELETE_RECIPE]


# Convenience function for easy integration
def classify_recipe_intent(query: str, context: Optional[Dict] = None) -> Tuple[RecipeIntent, float, str]:
    """
    Convenience function to classify recipe intent.
    
    Args:
        query: User query to classify
        context: Optional conversation context
        
    Returns:
        Tuple of (intent, confidence, reasoning)
    """
    classifier = RecipeIntentClassifier()
    return classifier.classify_intent(query, context)