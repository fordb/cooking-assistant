from src.examples import get_few_shot_examples

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