"""
Simple recipe extraction from conversational text.
"""

from typing import Optional, List
import re
from dataclasses import dataclass

from src.recipes.models import Recipe
from src.common.exceptions import CookingAssistantError


class RecipeExtractionError(CookingAssistantError):
    """Exception raised during recipe extraction."""
    pass


@dataclass 
class RecipeExtractionResult:
    """Result of recipe extraction."""
    success: bool
    recipe: Optional[Recipe] = None
    error: Optional[str] = None


class RecipeExtractor:
    """Simple recipe extraction from text."""
    
    def extract_recipe(self, text: str, recipe_name: Optional[str] = None) -> RecipeExtractionResult:
        """Extract recipe from text."""
        try:
            # Use provided name or extract from text
            title = recipe_name or self._extract_name(text)
            
            # Extract basic components
            ingredients = self._extract_bullet_points(text, is_ingredient=True)
            instructions = self._extract_numbered_steps(text)
            
            # Ensure minimum requirements with defaults
            if not ingredients:
                ingredients = ["Main ingredient", "Additional ingredient"]
            elif len(ingredients) < 2:
                ingredients.append("Additional ingredient")
                
            if not instructions:
                instructions = ["Prepare ingredients", "Cook as directed", "Serve when ready"]
            elif len(instructions) < 3:
                while len(instructions) < 3:
                    instructions.append(f"Complete step {len(instructions) + 1}")
            
            # Create recipe
            recipe = Recipe(
                title=title,
                ingredients=ingredients,
                instructions=instructions,
                prep_time=self._extract_time(text, "prep") or 10,
                cook_time=self._extract_time(text, "cook") or 20,
                servings=self._extract_servings(text) or 4,
                difficulty="Beginner"
            )
            
            return RecipeExtractionResult(success=True, recipe=recipe)
            
        except Exception as e:
            return RecipeExtractionResult(
                success=False,
                error=f"Extraction failed: {str(e)}"
            )
    
    def _extract_name(self, text: str) -> str:
        """Extract recipe name from text."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            first_line = lines[0]
            if 5 < len(first_line) < 50:
                return first_line
        return "Extracted Recipe"
    
    def _extract_bullet_points(self, text: str, is_ingredient: bool = True) -> List[str]:
        """Extract bullet point items."""
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if re.match(r'^[-*•]\s*(.+)', line):
                content = re.match(r'^[-*•]\s*(.+)', line).group(1).strip()
                if len(content) > 2:
                    items.append(content)
        return items
    
    def _extract_numbered_steps(self, text: str) -> List[str]:
        """Extract numbered instruction steps."""
        steps = []
        for line in text.split('\n'):
            line = line.strip()
            match = re.match(r'^\d+\.?\s*(.+)', line)
            if match:
                step = match.group(1).strip()
                if len(step) > 5:
                    steps.append(step)
        return steps
    
    def _extract_time(self, text: str, time_type: str) -> Optional[int]:
        """Extract prep or cook time."""
        pattern = f"{time_type}(?:\\s+time)?:?\\s*(\\d+)\\s*(?:min|minutes?)"
        match = re.search(pattern, text, re.IGNORECASE)
        return int(match.group(1)) if match else None
    
    def _extract_servings(self, text: str) -> Optional[int]:
        """Extract servings."""
        pattern = r"serves?:?\s*(\d+)|(\d+)\s*servings?"
        match = re.search(pattern, text, re.IGNORECASE)
        return int(match.group(1) or match.group(2)) if match else None


# Module-level singleton
_extractor: Optional[RecipeExtractor] = None


def get_recipe_extractor() -> RecipeExtractor:
    """Get singleton recipe extractor."""
    global _extractor
    if _extractor is None:
        _extractor = RecipeExtractor()
    return _extractor


# Convenience function
def extract_recipe_from_text(text: str, recipe_name: Optional[str] = None) -> RecipeExtractionResult:
    """Extract recipe from text."""
    return get_recipe_extractor().extract_recipe(text, recipe_name)