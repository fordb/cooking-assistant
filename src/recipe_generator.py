"""
Recipe generation module - backward compatibility wrapper.
Routes recipe generation through the meta-prompting system.
"""

from src.models import Recipe
from src.exceptions import RecipeGenerationError
from src.meta_prompting import process_cooking_query
import json

def generate_recipe(ingredients: str, template_type: str = "basic", **kwargs) -> Recipe:
    """
    Generate recipe using specified template.
    
    DEPRECATED: This function is maintained for backward compatibility.
    New code should use src.core.CookingAssistant.ask() instead.
    
    Args:
        ingredients: Comma-separated list of ingredients
        template_type: Type of recipe template to use
        **kwargs: Additional template parameters
        
    Returns:
        Recipe: Generated recipe object
        
    Raises:
        RecipeGenerationError: If recipe generation fails
    """
    
    try:
        # Construct query based on template type and parameters
        if template_type == "quick":
            max_time = kwargs.get("max_time", 30)
            query = f"Quick {max_time}-minute recipe using {ingredients}"
        elif template_type == "dietary":
            dietary_type = kwargs.get("dietary_type", "vegetarian")
            query = f"{dietary_type.title()} recipe using {ingredients}"
        elif template_type == "cuisine":
            cuisine = kwargs.get("cuisine", "Italian")
            query = f"{cuisine} recipe using {ingredients}"
        elif template_type == "substitution":
            original = kwargs.get("original_recipe", "recipe")
            missing = kwargs.get("missing", "ingredient")
            available = kwargs.get("available", ingredients)
            query = f"Modify {original} by substituting {missing} with {available}"
        else:  # basic
            query = f"Recipe using {ingredients}"
        
        # Use meta-prompting system to generate response
        result = process_cooking_query(query)
        
        if not result.get('success', True):
            raise RecipeGenerationError(f"Recipe generation failed: {result.get('error', 'Unknown error')}")
        
        # Try to parse response as JSON for Recipe object
        response_text = result['response']
        
        # Extract JSON from response if it contains other text
        try:
            # Look for JSON structure in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_text = response_text[start_idx:end_idx]
                recipe_data = json.loads(json_text)
                return Recipe(**recipe_data)
            else:
                # If no JSON found, return a basic recipe structure
                ingredient_list = [ing.strip() for ing in ingredients.split(',') if ing.strip()]
                if len(ingredient_list) < 2:
                    ingredient_list = [ingredients, "salt", "pepper"]  # Ensure minimum 2 ingredients
                
                return Recipe(
                    title=f"Recipe using {ingredients}",
                    prep_time=15,
                    cook_time=30,
                    servings=4,
                    difficulty="Intermediate",
                    ingredients=ingredient_list,
                    instructions=[
                        f"Use the ingredients: {ingredients}",
                        response_text[:200] + "..." if len(response_text) > 200 else response_text,
                        "Adjust seasoning and cooking time as needed"
                    ]
                )
                
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback: create basic recipe with response as instructions
            ingredient_list = [ing.strip() for ing in ingredients.split(',') if ing.strip()]
            if len(ingredient_list) < 2:
                ingredient_list = [ingredients, "salt", "pepper"]  # Ensure minimum 2 ingredients
                
            return Recipe(
                title=f"Recipe using {ingredients}",
                prep_time=15,
                cook_time=30,
                servings=4,
                difficulty="Intermediate", 
                ingredients=ingredient_list,
                instructions=[
                    f"Generated response: {response_text[:500]}...",
                    "Follow cooking instructions as provided",
                    "Adjust seasoning and timing to taste"
                ]
            )
            
    except Exception as e:
        raise RecipeGenerationError(f"Failed to generate recipe: {e}")