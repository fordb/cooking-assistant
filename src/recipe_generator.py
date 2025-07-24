from openai import OpenAI
from config import OPENAI_API_KEY
from src.prompts import create_basic_recipe_prompt
from src.models import Recipe
from src.output_validator import validate_recipe_structure, validate_measurements
from src.safety_validator import validate_recipe_safety
import json

def generate_basic_recipe(ingredients: str) -> Recipe:
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = create_basic_recipe_prompt(ingredients)
    
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