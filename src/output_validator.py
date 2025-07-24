from src.models import Recipe
from typing import Tuple, List

def validate_recipe_structure(recipe_data: dict) -> Tuple[bool, List[str]]:
    """Validate recipe has all required fields and proper format."""
    errors = []
    
    try:
        recipe = Recipe(**recipe_data)
    except Exception as e:
        errors.append(f"Schema validation failed: {str(e)}")
        return False, errors
    
    # Additional validation
    if recipe.prep_time < 0 or recipe.cook_time < 0:
        errors.append("Prep/cook times must be positive")
    
    if recipe.servings < 1 or recipe.servings > 20:
        errors.append("Servings must be between 1-20")
        
    if len(recipe.ingredients) < 2:
        errors.append("Recipe must have at least 2 ingredients")
        
    if len(recipe.instructions) < 3:
        errors.append("Recipe must have at least 3 instruction steps")
    
    return len(errors) == 0, errors

def validate_measurements(ingredients: List[str]) -> Tuple[bool, List[str]]:
    """Check ingredients have realistic measurements."""
    errors = []
    measurement_words = ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce', 'gram', 'piece', 'clove']
    
    for ingredient in ingredients:
        has_measurement = any(word in ingredient.lower() for word in measurement_words)
        has_number = any(char.isdigit() for char in ingredient)
        
        if not (has_measurement or has_number):
            errors.append(f"Ingredient missing measurement: {ingredient}")
    
    return len(errors) == 0, errors