from src.examples import get_few_shot_examples

TEMPLATE_TYPES = {
    "basic": "General recipe generation",
    "quick": "Quick meals under 30 minutes", 
    "dietary": "Specific dietary restrictions",
    "cuisine": "Specific cuisine style",
    "substitution": "Ingredient substitutions"
}

def create_basic_recipe_prompt(ingredients: str) -> str:
    examples = get_few_shot_examples(3)
    
    return f"""You are an expert chef. Create a recipe using the provided ingredients.

    Here are examples of perfect recipe format:

    {examples}

    Now create a recipe using these ingredients: {ingredients}

    Requirements:
    - Use realistic measurements and cooking times
    - Include proper cooking techniques
    - Ensure food safety (proper temperatures, safe combinations)
    - Format as valid JSON matching the examples exactly
    - Make it practical for home cooking

    Return only the JSON recipe, no other text."""

def create_quick_meal_prompt(ingredients: str, max_time: int = 30) -> str:
    examples = get_few_shot_examples(2)  # Use fewer for speed
    return f"""Create a quick meal recipe using: {ingredients}
    
    {examples}
    
    CONSTRAINTS:
    - Total time (prep + cook) must be under {max_time} minutes
    - Use simple cooking techniques (no complex prep)
    - Minimize cleanup and dishes used
    - Focus on efficiency and speed
    
    Return only JSON recipe matching the example format."""

def create_dietary_prompt(ingredients: str, dietary_type: str) -> str:
    examples = get_few_shot_examples(2)
    return f"""Create a {dietary_type} recipe using: {ingredients}
    
    {examples}
    
    DIETARY REQUIREMENTS:
    - Must be completely {dietary_type}
    - Check all ingredients for compliance
    - Suggest substitutions if needed
    - Include nutritional considerations
    
    Return only JSON recipe matching the example format."""

def create_cuisine_prompt(ingredients: str, cuisine: str) -> str:
    examples = get_few_shot_examples(2)
    return f"""Create a {cuisine} style recipe using: {ingredients}
    
    {examples}
    
    CUISINE REQUIREMENTS:
    - Use authentic {cuisine} cooking techniques
    - Include traditional seasonings and flavors
    - Respect cultural cooking methods
    - Make it accessible for home cooking
    
    Return only JSON recipe matching the example format."""

def create_substitution_prompt(original_recipe: str, missing_ingredients: str, available_ingredients: str) -> str:
    return f"""Modify this recipe by substituting ingredients:
    
    Original Recipe: {original_recipe}
    Missing: {missing_ingredients}  
    Available: {available_ingredients}
    
    Create a new recipe with substitutions that maintains similar flavors and cooking method.
    
    Return only JSON recipe in standard format."""

def select_prompt_template(template_type: str, **kwargs) -> str:
    if template_type == "basic":
        return create_basic_recipe_prompt(kwargs["ingredients"])
    elif template_type == "quick":
        return create_quick_meal_prompt(kwargs["ingredients"], kwargs.get("max_time", 30))
    elif template_type == "dietary":
        return create_dietary_prompt(kwargs["ingredients"], kwargs["dietary_type"])
    elif template_type == "cuisine":
        return create_cuisine_prompt(kwargs["ingredients"], kwargs["cuisine"])
    elif template_type == "substitution":
        return create_substitution_prompt(kwargs["original_recipe"], kwargs["missing"], kwargs["available"])
    else:
        raise ValueError(f"Unknown template type: {template_type}")