from src.examples import get_few_shot_examples
from src.exceptions import TemplateError

TEMPLATE_TYPES = {
    "basic": "General recipe generation",
    "quick": "Quick meals under 30 minutes", 
    "dietary": "Specific dietary restrictions",
    "cuisine": "Specific cuisine style",
    "substitution": "Ingredient substitutions"
}

def create_basic_recipe_prompt(ingredients: str, skill_level: str = "intermediate") -> str:
    ingredient_list = [ing.strip() for ing in ingredients.split(',') if ing.strip()]
    few_shot_examples = get_few_shot_examples(3)
    
    return f"""You are an expert chef and recipe developer. Create a delicious, practical recipe using the provided ingredients.

=== INGREDIENTS TO USE ===
{', '.join(ingredient_list)}

=== EXAMPLE RECIPES FOR REFERENCE ===
{few_shot_examples}

=== RECIPE REQUIREMENTS ===
• Use ALL provided ingredients as main components (not just garnishes)
• Suggest common pantry staples (salt, pepper, oil, etc.) if needed
• Provide realistic prep time (5-45 min) and cook time (10-120 min)
• Include serving size (1-8 people)
• Use proper cooking techniques with clear instructions
• Ensure food safety (internal temperatures, safe ingredient combinations)
• Scale measurements appropriately for serving size
• Make it achievable for {skill_level} level cooks

=== SAFETY REQUIREMENTS ===
• Never suggest raw or undercooked meat/eggs without proper safety warnings
• Avoid dangerous ingredient combinations
• Include internal temperature guidelines for meat dishes
• Suggest proper food storage if relevant

=== QUALITY STANDARDS ===
• Balance flavors (sweet, salty, sour, bitter, umami)
• Consider texture variety
• Ensure nutritional balance when possible
• Make the recipe sound appetizing and achievable

=== OUTPUT FORMAT ===
Return ONLY valid JSON matching this exact structure:
{{
    "name": "Recipe Name",
    "description": "Brief appetizing description",
    "prep_time_minutes": number,
    "cook_time_minutes": number,
    "servings": number,
    "difficulty": "easy|medium|hard",
    "ingredients": [
        {{"item": "ingredient name", "amount": "quantity", "unit": "measurement"}}
    ],
    "instructions": [
        "Step 1 instruction",
        "Step 2 instruction"
    ],
    "tips": ["helpful cooking tip"],
    "nutrition_notes": "brief nutritional highlights"
}}"""

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
    """Select and create appropriate prompt template."""
    if template_type not in TEMPLATE_TYPES:
        raise TemplateError(f"Unknown template type: {template_type}. Valid options: {list(TEMPLATE_TYPES.keys())}")
    
    try:
        if template_type == "basic":
            return create_basic_recipe_prompt(kwargs["ingredients"], kwargs.get("skill_level", "intermediate"))
        elif template_type == "quick":
            return create_quick_meal_prompt(kwargs["ingredients"], kwargs.get("max_time", 30))
        elif template_type == "dietary":
            return create_dietary_prompt(kwargs["ingredients"], kwargs["dietary_type"])
        elif template_type == "cuisine":
            return create_cuisine_prompt(kwargs["ingredients"], kwargs["cuisine"])
        elif template_type == "substitution":
            return create_substitution_prompt(kwargs["original_recipe"], kwargs["missing"], kwargs["available"])
    except KeyError as e:
        raise TemplateError(f"Missing required parameter for {template_type} template: {e}")
    except Exception as e:
        raise TemplateError(f"Error creating {template_type} template: {e}")