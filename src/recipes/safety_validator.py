from openai import OpenAI
from .models import SafetyValidation, Recipe
from src.common.exceptions import SafetyValidationError
import json

SAFETY_PROMPT = """Analyze this recipe for safety issues:

Recipe: {recipe}

Check for:
- Dangerous ingredient combinations
- Unsafe cooking temperatures for meat/poultry
- Unrealistic or dangerous cooking times
- Missing critical safety steps (washing hands, proper storage)
- Raw food handling issues

Return JSON in this exact format:
{{
  "safe": true/false,
  "warnings": ["list of specific safety concerns if any"]
}}

Return only the JSON, no other text."""

def validate_recipe_safety(recipe: Recipe) -> SafetyValidation:
    """Validate recipe safety using AI analysis."""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        recipe_text = f"""
        Title: {recipe.title}
        Ingredients: {', '.join(recipe.ingredients)}
        Instructions: {'. '.join(recipe.instructions)}
        """
        
        prompt = SAFETY_PROMPT.format(recipe=recipe_text)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1  # Low temperature for consistent safety checking
        )
        
        safety_json = response.choices[0].message.content
        safety_data = json.loads(safety_json)
        return SafetyValidation(**safety_data)
        
    except json.JSONDecodeError as e:
        raise SafetyValidationError(f"Failed to parse safety validation JSON: {e}")
    except Exception as e:
        raise SafetyValidationError(f"Safety validation failed: {e}")