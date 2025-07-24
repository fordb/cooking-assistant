from openai import OpenAI
from config import OPENAI_API_KEY
from src.prompts import select_prompt_template, TEMPLATE_TYPES
from src.models import Recipe
from src.output_validator import validate_recipe_structure, validate_measurements
from src.safety_validator import validate_recipe_safety
import json

def generate_recipe(ingredients: str, template_type: str = "basic", **kwargs) -> Recipe:
    """Generate recipe using specified template."""

    if template_type not in TEMPLATE_TYPES:
        raise ValueError(f"Invalid template type. Options: {list(TEMPLATE_TYPES.keys())}")

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = select_prompt_template(template_type, ingredients=ingredients, **kwargs)
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    recipe_json = response.choices[0].message.content
    recipe_data = json.loads(recipe_json)
    
    # Validate structure
    is_valid, errors = validate_recipe_structure(recipe_data)
    if not is_valid:
        raise ValueError(f"Recipe validation failed: {errors}")
    
    recipe = Recipe(**recipe_data)
    
    # Validate measurements
    is_valid, errors = validate_measurements(recipe.ingredients)
    if not is_valid:
        print(f"Measurement warnings: {errors}")
    
    # Validate safety
    safety_result = validate_recipe_safety(recipe)
    if not safety_result.safe:
        print(f"Safety warnings: {safety_result.warnings}")
    
    return recipe