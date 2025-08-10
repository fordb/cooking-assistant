"""
Simple recipe coordinator for conversational recipe management.
"""

from typing import Optional
from dataclasses import dataclass

from src.core.recipe_intent_classifier import classify_recipe_intent, RecipeIntent
from src.core.user_identity import get_identity_manager, UserProfile
from src.core.recipe_extractor import extract_recipe_from_text
from src.recipes.models import Recipe


@dataclass
class RecipeResult:
    """Simple result from recipe coordination."""
    success: bool
    intent: Optional[RecipeIntent] = None
    user: Optional[UserProfile] = None
    recipe: Optional[Recipe] = None
    message: str = ""


class RecipeCoordinator:
    """Coordinates recipe operations."""
    
    def __init__(self):
        self.identity_manager = get_identity_manager()
    
    def process(self, text: str, session_id: Optional[str] = None) -> RecipeResult:
        """Process user input through recipe pipeline."""
        try:
            # Classify intent
            intent, confidence, _ = classify_recipe_intent(text)
            
            # Get or create user
            user = None
            if session_id:
                user = self.identity_manager.get_user_from_session(session_id)
            if not user:
                user = self.identity_manager.create_user()
                self.identity_manager.create_session(user.user_id)
            
            # Handle recipe creation
            if intent == RecipeIntent.REGULAR_COOKING:
                extraction = extract_recipe_from_text(text)
                if extraction.success:
                    self.identity_manager.increment_recipe_count(user.user_id)
                    return RecipeResult(
                        success=True,
                        intent=intent,
                        user=user,
                        recipe=extraction.recipe,
                        message=f"Created recipe: {extraction.recipe.title}"
                    )
                return RecipeResult(False, intent, user, message="Could not extract recipe")
            
            # Handle other intents
            return RecipeResult(
                success=True,
                intent=intent,
                user=user,
                message=f"Understood: {intent.value} (not yet implemented)"
            )
            
        except Exception as e:
            return RecipeResult(False, message=f"Error: {str(e)}")


# Singleton
_coordinator: Optional[RecipeCoordinator] = None


def process_recipe_input(text: str, session_id: Optional[str] = None) -> RecipeResult:
    """Process recipe input through coordinator."""
    global _coordinator
    if _coordinator is None:
        _coordinator = RecipeCoordinator()
    return _coordinator.process(text, session_id)