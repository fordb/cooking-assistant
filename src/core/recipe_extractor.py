"""
LLM-based recipe extraction from conversational text.
"""

from typing import Optional
import json
import os
from dataclasses import dataclass
from openai import OpenAI

from src.recipes.models import Recipe
from src.common.exceptions import CookingAssistantError
from src.common.config import get_openai_config, get_logger

logger = get_logger(__name__)


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
    """LLM-based recipe extraction from text."""
    
    def __init__(self):
        """Initialize with OpenAI client."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise RecipeExtractionError("OpenAI API key not found")
        
        self.client = OpenAI(api_key=api_key)
        self.config = get_openai_config()
    
    def extract_recipe(self, text: str, recipe_name: Optional[str] = None) -> RecipeExtractionResult:
        """Extract recipe using LLM structured extraction."""
        try:
            # Build extraction prompt
            prompt = self._build_extraction_prompt(text, recipe_name)
            
            # Get LLM response
            response = self.client.chat.completions.create(
                model=self.config.DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse JSON response
            result_text = response.choices[0].message.content.strip()
            recipe_data = self._parse_json_response(result_text)
            
            # Create Recipe object
            recipe = Recipe(
                title=recipe_data.get("title", "Extracted Recipe"),
                ingredients=recipe_data.get("ingredients", ["Main ingredient", "Additional ingredient"]),
                instructions=recipe_data.get("instructions", ["Prepare ingredients", "Cook as directed", "Serve when ready"]),
                prep_time=recipe_data.get("prep_time", 10),
                cook_time=recipe_data.get("cook_time", 20),
                servings=recipe_data.get("servings", 4),
                difficulty="Beginner"
            )
            
            return RecipeExtractionResult(success=True, recipe=recipe)
            
        except Exception as e:
            logger.error(f"Recipe extraction failed: {str(e)}")
            return RecipeExtractionResult(
                success=False,
                error=f"Extraction failed: {str(e)}"
            )
    
    def _build_extraction_prompt(self, text: str, recipe_name: Optional[str] = None) -> str:
        """Build prompt for LLM-based recipe extraction."""
        name_instruction = f' Use "{recipe_name}" as the title.' if recipe_name else ''
        
        return f"""Extract recipe information from the following text and return it as valid JSON.{name_instruction}

Required JSON format:
{{
  "title": "recipe name",
  "ingredients": ["ingredient with amount", "another ingredient"],
  "instructions": ["step 1", "step 2", "step 3"],
  "prep_time": 10,
  "cook_time": 20, 
  "servings": 4
}}

Rules:
- Extract ALL ingredients with their amounts/measurements
- Extract ALL instruction steps in order
- If prep_time, cook_time, or servings aren't specified, estimate reasonable values
- Ensure at least 2 ingredients and 3 instruction steps
- Keep ingredient and instruction text clear and concise

Text to extract from:
{text}

Return only the JSON object:"""
    
    def _parse_json_response(self, response_text: str) -> dict:
        """Parse JSON response from LLM, with fallback handling."""
        try:
            # Try to extract JSON from response
            response_text = response_text.strip()
            
            # Handle cases where LLM adds extra text
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            
            # Try to find JSON object bounds
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                response_text = response_text[start:end]
            
            return json.loads(response_text)
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse JSON response: {e}. Response: {response_text}")
            # Return minimal valid structure
            return {
                "title": "Extracted Recipe",
                "ingredients": ["Main ingredient", "Additional ingredient"],
                "instructions": ["Prepare ingredients", "Cook as directed", "Serve when ready"],
                "prep_time": 10,
                "cook_time": 20,
                "servings": 4
            }


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