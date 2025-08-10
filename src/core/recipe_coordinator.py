"""
Recipe management coordinator for conversational recipe management.
Integrates intent classification, user identity, and recipe extraction.
"""

from typing import Optional, Union
from dataclasses import dataclass
from enum import Enum

from src.core.recipe_intent_classifier import classify_recipe_intent, RecipeIntent
from src.core.user_identity import get_identity_manager, UserProfile
from src.core.recipe_extractor import extract_recipe_from_text, RecipeExtractionResult
from src.recipes.models import Recipe
from src.common.exceptions import CookingAssistantError
from src.common.config import get_logger

logger = get_logger(__name__)


class RecipeCoordinatorError(CookingAssistantError):
    """Exception raised during recipe coordination operations."""
    pass


class CoordinationStatus(Enum):
    """Status of recipe coordination operation."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class CoordinationResult:
    """Result of recipe coordination operation."""
    status: CoordinationStatus
    intent: Optional[RecipeIntent] = None
    user: Optional[UserProfile] = None
    recipe: Optional[Recipe] = None
    message: Optional[str] = None
    error: Optional[str] = None


class RecipeCoordinator:
    """Coordinates recipe operations across intent classification, user management, and extraction."""
    
    def __init__(self):
        """Initialize coordinator."""
        self.identity_manager = get_identity_manager()
    
    def process_user_input(self, text: str, session_id: Optional[str] = None) -> CoordinationResult:
        """Process user input through full pipeline."""
        try:
            # Step 1: Classify intent
            intent, confidence, reasoning = classify_recipe_intent(text)
            logger.info(f"Classified intent: {intent} (confidence: {confidence})")
            
            # Step 2: Handle user identity
            user = None
            if session_id:
                user = self.identity_manager.get_user_from_session(session_id)
            
            if not user:
                # Create new user and session if needed
                user = self.identity_manager.create_user()
                session_id = self.identity_manager.create_session(user.user_id)
                logger.info(f"Created new user: {user.user_id}")
            
            # Step 3: Handle based on intent
            if intent == RecipeIntent.REGULAR_COOKING:
                return self._handle_recipe_creation(text, user)
            elif intent == RecipeIntent.FIND_RECIPES:
                return self._handle_recipe_search(text, user)
            elif intent == RecipeIntent.SAVE_RECIPE:
                return self._handle_recipe_save(text, user)
            elif intent == RecipeIntent.LIST_RECIPES:
                return self._handle_recipe_list(text, user)
            elif intent == RecipeIntent.DELETE_RECIPE:
                return self._handle_recipe_deletion(text, user)
            else:
                return CoordinationResult(
                    status=CoordinationStatus.SUCCESS,
                    intent=intent,
                    user=user,
                    message=f"Recognized intent: {intent.value}. How can I help you with recipes?"
                )
        
        except Exception as e:
            logger.error(f"Recipe coordination failed: {str(e)}")
            return CoordinationResult(
                status=CoordinationStatus.FAILED,
                error=f"Coordination failed: {str(e)}"
            )
    
    def _handle_recipe_creation(self, text: str, user: UserProfile) -> CoordinationResult:
        """Handle recipe creation requests."""
        extraction_result = extract_recipe_from_text(text)
        
        if not extraction_result.success:
            return CoordinationResult(
                status=CoordinationStatus.FAILED,
                intent=RecipeIntent.REGULAR_COOKING,
                user=user,
                error="Failed to extract recipe from text"
            )
        
        # Increment user's recipe count
        self.identity_manager.increment_recipe_count(user.user_id)
        
        return CoordinationResult(
            status=CoordinationStatus.SUCCESS,
            intent=RecipeIntent.REGULAR_COOKING,
            user=user,
            recipe=extraction_result.recipe,
            message=f"Successfully created recipe: {extraction_result.recipe.title}"
        )
    
    def _handle_recipe_search(self, text: str, user: UserProfile) -> CoordinationResult:
        """Handle recipe search requests."""
        return CoordinationResult(
            status=CoordinationStatus.PARTIAL,
            intent=RecipeIntent.FIND_RECIPES,
            user=user,
            message="Recipe search functionality will be implemented in future commits"
        )
    
    def _handle_recipe_save(self, text: str, user: UserProfile) -> CoordinationResult:
        """Handle recipe save requests."""
        return CoordinationResult(
            status=CoordinationStatus.PARTIAL,
            intent=RecipeIntent.SAVE_RECIPE,
            user=user,
            message="Recipe save functionality will be implemented in future commits"
        )
    
    def _handle_recipe_list(self, text: str, user: UserProfile) -> CoordinationResult:
        """Handle recipe list requests."""
        return CoordinationResult(
            status=CoordinationStatus.PARTIAL,
            intent=RecipeIntent.LIST_RECIPES,
            user=user,
            message="Recipe list functionality will be implemented in future commits"
        )
    
    def _handle_recipe_deletion(self, text: str, user: UserProfile) -> CoordinationResult:
        """Handle recipe deletion requests."""
        return CoordinationResult(
            status=CoordinationStatus.PARTIAL,
            intent=RecipeIntent.DELETE_RECIPE,
            user=user,
            message="Recipe deletion functionality will be implemented in future commits"
        )


# Module-level singleton
_coordinator: Optional[RecipeCoordinator] = None


def get_recipe_coordinator() -> RecipeCoordinator:
    """Get singleton recipe coordinator."""
    global _coordinator
    if _coordinator is None:
        _coordinator = RecipeCoordinator()
    return _coordinator


# Convenience function
def process_recipe_input(text: str, session_id: Optional[str] = None) -> CoordinationResult:
    """Process recipe input through coordinator."""
    return get_recipe_coordinator().process_user_input(text, session_id)