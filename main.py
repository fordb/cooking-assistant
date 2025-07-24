import argparse
from src.recipe_generator import generate_recipe
from src.prompts import TEMPLATE_TYPES


def interactive_mode():
    print("🧑‍🍳 Welcome to AI Recipe Generator!")
    
    while True:
        ingredients = input("\nWhat ingredients do you have? (or 'quit'): ")
        if ingredients.lower() == 'quit':
            break

        recipe_type = input(f"Recipe type ({'/'.join(TEMPLATE_TYPES.keys())}): ") or "basic"
        
        try:
            recipe = generate_recipe(ingredients, recipe_type)
            print(recipe.model_dump_json(indent=2))
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    interactive_mode()