"""
Simple recipe extraction from conversational text.
"""

from typing import Optional
import json
import os
from dataclasses import dataclass
from openai import OpenAI

from src.recipes.models import Recipe


@dataclass 
class RecipeExtractionResult:
    """Result of recipe extraction."""
    success: bool
    recipe: Optional[Recipe] = None
    error: Optional[str] = None


class RecipeExtractor:
    """Extract recipes from text using LLM."""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key required")
        self.client = OpenAI(api_key=api_key)
    
    def extract_recipe(self, text: str, recipe_name: Optional[str] = None) -> RecipeExtractionResult:
        """Extract recipe from text."""
        try:
            prompt = self._build_prompt(text, recipe_name)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            result_text = response.choices[0].message.content.strip()
            recipe_data = self._parse_json(result_text)
            
            recipe = Recipe(
                title=recipe_data.get("title", "Extracted Recipe"),
                ingredients=recipe_data.get("ingredients", ["Main ingredient", "Additional ingredient"]),
                instructions=recipe_data.get("instructions", ["Prepare", "Cook", "Serve"]),
                prep_time=recipe_data.get("prep_time", 10),
                cook_time=recipe_data.get("cook_time", 20),
                servings=recipe_data.get("servings", 4),
                difficulty="Beginner"
            )
            
            return RecipeExtractionResult(success=True, recipe=recipe)
            
        except Exception as e:
            return RecipeExtractionResult(success=False, error=str(e))
    
    def _build_prompt(self, text: str, recipe_name: Optional[str] = None) -> str:
        """Build extraction prompt."""
        name_part = f' Use "{recipe_name}" as title.' if recipe_name else ''
        
        return f"""Extract recipe from this text as JSON:{name_part}

{{
  "title": "recipe name",
  "ingredients": ["ingredient with amount", "another ingredient"],
  "instructions": ["step 1", "step 2", "step 3"],
  "prep_time": 10,
  "cook_time": 20,
  "servings": 4
}}

Text: {text}

JSON:"""
    
    def _parse_json(self, response_text: str) -> dict:
        """Parse JSON from response."""
        try:
            # Clean up response
            text = response_text.strip()
            
            # Remove code blocks
            if '```json' in text:
                start = text.find('```json') + 7
                end = text.find('```', start)
                text = text[start:end].strip()
            elif '```' in text:
                start = text.find('```') + 3
                end = text.find('```', start)
                text = text[start:end].strip()
            
            # Find JSON object
            if '{' in text and '}' in text:
                start = text.find('{')
                end = text.rfind('}') + 1
                text = text[start:end]
            
            return json.loads(text)
            
        except:
            # Fallback
            return {
                "title": "Extracted Recipe",
                "ingredients": ["Main ingredient", "Additional ingredient"],
                "instructions": ["Prepare", "Cook", "Serve"],
                "prep_time": 10,
                "cook_time": 20,
                "servings": 4
            }


# Singleton
_extractor: Optional[RecipeExtractor] = None


def extract_recipe_from_text(text: str, recipe_name: Optional[str] = None) -> RecipeExtractionResult:
    """Extract recipe from text."""
    global _extractor
    if _extractor is None:
        _extractor = RecipeExtractor()
    return _extractor.extract_recipe(text, recipe_name)