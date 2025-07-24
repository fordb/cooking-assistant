import argparse
from src.recipe_generator import generate_recipe
from src.prompts import TEMPLATE_TYPES, select_prompt_template
from src.examples import load_example_recipes, get_few_shot_examples
from src.exceptions import CookingAssistantError


def test_examples():
    """Load and display example recipes."""
    print("🧑‍🍳 Loading Example Recipes")
    print("=" * 50)
    
    try:
        recipes = load_example_recipes()
        print(f"Loaded {len(recipes)} example recipes:")
        
        for i, recipe in enumerate(recipes[:5], 1):  # Show first 5
            print(f"\n{i}. {recipe.title}")
            print(f"   Difficulty: {recipe.difficulty} | Time: {recipe.total_time} min | Serves: {recipe.servings}")
            print(f"   Ingredients: {len(recipe.ingredients)} | Steps: {len(recipe.instructions)}")
            
    except Exception as e:
        print(f"❌ Error loading examples: {e}")


def test_prompt_templates():
    """Demonstrate all prompt template types."""
    print("\n🧑‍🍳 Testing Prompt Templates")
    print("=" * 50)
    
    ingredients = "chicken, rice, vegetables"
    
    for template_type, description in TEMPLATE_TYPES.items():
        print(f"\n{template_type.upper()} Template ({description}):")
        print("-" * 40)
        
        try:
            if template_type == "dietary":
                prompt = select_prompt_template(template_type, ingredients=ingredients, dietary_type="vegetarian")
            elif template_type == "cuisine":
                prompt = select_prompt_template(template_type, ingredients=ingredients, cuisine="Italian")
            elif template_type == "substitution":
                prompt = select_prompt_template(template_type, 
                                              original_recipe="Chicken Rice Bowl",
                                              missing="chicken",
                                              available="tofu")
            else:
                prompt = select_prompt_template(template_type, ingredients=ingredients)
            
            # Show first 200 characters of prompt
            print(f"Prompt preview: {prompt[:200]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")


def show_template_usage():
    """Show usage examples for each template type."""
    print("\n🧑‍🍳 Template Usage Guide")
    print("=" * 50)
    
    usage_examples = {
        "basic": "general recipe generation with any ingredients",
        "quick": "meals that can be prepared in under 30 minutes",
        "dietary": "recipes for specific dietary needs (vegetarian, vegan, gluten-free, etc.)",
        "cuisine": "recipes in specific cuisine styles (Italian, Mexican, Asian, etc.)",
        "substitution": "modify existing recipes by substituting unavailable ingredients"
    }
    
    for template_type, usage in usage_examples.items():
        print(f"\n{template_type.upper()}: {usage}")


def interactive_mode():
    """Interactive recipe generation mode."""
    print("🧑‍🍳 Welcome to AI Recipe Generator!")
    print("Type 'help' for template options, 'examples' to see example recipes, or 'quit' to exit.")
    
    while True:
        print("\n" + "-" * 50)
        ingredients = input("What ingredients do you have? ")
        
        if ingredients.lower() == 'quit':
            print("👋 Happy cooking!")
            break
        elif ingredients.lower() == 'help':
            show_template_usage()
            continue
        elif ingredients.lower() == 'examples':
            test_examples()
            continue
        
        recipe_type = input(f"Recipe type ({'/'.join(TEMPLATE_TYPES.keys())}): ") or "basic"
        
        try:
            print("\n🔄 Generating recipe...")
            recipe = generate_recipe(ingredients, recipe_type)
            
            print("\n✅ Recipe Generated!")
            print("=" * 50)
            print(recipe.model_dump_json(indent=2))
            
        except CookingAssistantError as e:
            print(f"❌ Recipe Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")


def main():
    """Main entry point with command line argument support."""
    parser = argparse.ArgumentParser(description="AI Recipe Generator")
    parser.add_argument("--test-examples", action="store_true", help="Test example recipe loading")
    parser.add_argument("--test-templates", action="store_true", help="Test prompt templates")
    parser.add_argument("--show-usage", action="store_true", help="Show template usage guide")
    
    args = parser.parse_args()
    
    if args.test_examples:
        test_examples()
    elif args.test_templates:
        test_prompt_templates()
    elif args.show_usage:
        show_template_usage()
    else:
        interactive_mode()


if __name__ == "__main__":
    main()