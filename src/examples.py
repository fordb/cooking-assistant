import json
from typing import List
from src.models import Recipe
from config import EXAMPLE_RECIPES_PATH

def load_example_recipes() -> List[Recipe]:
    """Load example recipes from the configured path."""
    with open(EXAMPLE_RECIPES_PATH, 'r') as f:
        data = json.load(f)
    return [Recipe(**recipe) for recipe in data]

def get_few_shot_examples(num_examples: int = 3) -> str:
    examples = load_example_recipes()[:num_examples]
    formatted = []
    for recipe in examples:
        formatted.append(f"Example Recipe:\n{recipe.model_dump_json(indent=2)}")
    return "\n\n".join(formatted)