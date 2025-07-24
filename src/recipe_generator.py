from openai import OpenAI
from config import OPENAI_API_KEY
from src.prompts import select_prompt_template
from src.models import Recipe
from src.safety_validator import validate_recipe_safety
from src.exceptions import RecipeGenerationError, TemplateError
import json

def generate_recipe(ingredients: str, template_type: str = "basic", **kwargs) -> Recipe:
    """Generate recipe using specified template."""
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = select_prompt_template(template_type, ingredients=ingredients, **kwargs)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        recipe_json = response.choices[0].message.content
        recipe_data = json.loads(recipe_json)
        
        # Create recipe - validation happens automatically in Recipe model
        recipe = Recipe(**recipe_data)
        
        # Validate safety (keeping GenAI-based safety validation)
        safety_result = validate_recipe_safety(recipe)
        if not safety_result.safe:
            print(f"Safety warnings: {safety_result.warnings}")
        
        return recipe
        
    except TemplateError:
        # Re-raise template errors as-is
        raise
    except json.JSONDecodeError as e:
        raise RecipeGenerationError(f"Failed to parse recipe JSON: {e}")
    except Exception as e:
        raise RecipeGenerationError(f"Failed to generate recipe: {e}")