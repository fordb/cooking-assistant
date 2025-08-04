import json
from typing import List
from src.recipes.models import Recipe

def load_example_recipes() -> List[Recipe]:
    """Load example recipes from the configured path."""
    # Use hardcoded path since it's standardized
    example_recipes_path = 'data/example_recipes.json'
    with open(example_recipes_path, 'r') as f:
        data = json.load(f)
    return [Recipe(**recipe) for recipe in data]

def get_few_shot_examples(num_examples: int = 3) -> str:
    examples = load_example_recipes()[:num_examples]
    formatted = []
    for recipe in examples:
        formatted.append(f"Example Recipe:\n{recipe.model_dump_json(indent=2)}")
    return "\n\n".join(formatted)