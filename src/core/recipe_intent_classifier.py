"""
LLM-based recipe intent classifier for conversational recipe management.
Uses flexible few-shot prompting to detect user intentions for recipe operations.
"""

from typing import Dict, Any, Tuple, Optional
from enum import Enum
import os
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
        """Build focused few-shot classification prompt."""
        
        context_info = ""
        if context and context.get('recent_recipes'):
            context_info = f"\nContext: User recently discussed {', '.join(context['recent_recipes'])}"
        
        return f"""Classify this cooking query into one category:

SAVE_RECIPE: Save/store/remember a recipe
FIND_RECIPES: Search for specific saved recipes  
LIST_RECIPES: Show all saved recipes
DELETE_RECIPE: Remove/delete a saved recipe
REGULAR_COOKING: Recipe generation or cooking advice

Examples:
"Save this recipe" → SAVE_RECIPE (0.95) Clear save request
"Show my pasta recipes" → FIND_RECIPES (0.95) Search user collection
"What recipes do I have?" → LIST_RECIPES (0.95) List all saved
"Delete this recipe" → DELETE_RECIPE (0.90) Remove from collection
"How do I make soup?" → REGULAR_COOKING (0.95) Recipe generation{context_info}

Query: "{query}"

Format: Intent: [INTENT] | Confidence: [0.0-1.0] | Reasoning: [brief explanation]"""

    def _parse_classification_result(self, result: str) -> Tuple[RecipeIntent, float, str]:
        """Parse the LLM classification result."""
        try:
            # Handle both old format (multiline) and new format (single line with |)
            if '|' in result:
                # New compact format: Intent: SAVE_RECIPE | Confidence: 0.95 | Reasoning: explanation
                parts = result.strip().split('|')
                intent_str = parts[0].replace('Intent:', '').strip() if len(parts) > 0 else None
                confidence_str = parts[1].replace('Confidence:', '').strip() if len(parts) > 1 else '0.5'
                reasoning = parts[2].replace('Reasoning:', '').strip() if len(parts) > 2 else 'No reasoning'
                
                try:
                    confidence = float(confidence_str)
                except ValueError:
                    confidence = 0.5
            else:
                # Old multiline format
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