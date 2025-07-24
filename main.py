from openai import OpenAI
from config import OPENAI_API_KEY
from src.models import Recipe
from src.examples import load_example_recipes, get_few_shot_examples
from src.recipe_generator import generate_basic_recipe
from src.prompts import select_prompt_template, TEMPLATE_TYPES

def test_connection():
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hello"}]
    )
    print("Connection successful:", response.choices[0].message.content)

def test_model():
    sample = {
        "title": "Test Recipe",
        "prep_time": 10,
        "cook_time": 20,
        "servings": 2,
        "difficulty": "Beginner", 
        "ingredients": ["1 cup rice"],
        "instructions": ["Cook rice"]
    }
    recipe = Recipe(**sample)
    print("Model validation successful:", recipe.title)

def test_examples():    
    few_shot = get_few_shot_examples(5)
    print(few_shot)

def test_basic_generation():
    recipe = generate_basic_recipe("chicken, rice, broccoli")
    print(recipe)

def test_prompt_templates():
    """Test different prompt template types"""
    print("Available template types:")
    for template_type, description in TEMPLATE_TYPES.items():
        print(f"  {template_type}: {description}")
    
    print("\n" + "="*50)
    
    # Test basic template
    print("BASIC TEMPLATE:")
    basic_prompt = select_prompt_template("basic", ingredients="pasta, tomatoes, garlic")
    print(basic_prompt[:200] + "...")
    
    print("\n" + "="*50)
    
    # Test quick meal template
    print("QUICK MEAL TEMPLATE:")
    quick_prompt = select_prompt_template("quick", ingredients="eggs, bread, cheese", max_time=15)
    print(quick_prompt[:200] + "...")
    
    print("\n" + "="*50)
    
    # Test cuisine template
    print("CUISINE TEMPLATE:")
    cuisine_prompt = select_prompt_template("cuisine", ingredients="rice, soy sauce, vegetables", cuisine="Asian")
    print(cuisine_prompt[:200] + "...")
    
    print("\n" + "="*50)
    
    # Test dietary template
    print("DIETARY TEMPLATE:")
    dietary_prompt = select_prompt_template("dietary", ingredients="beans, vegetables, quinoa", dietary_type="vegan")
    print(dietary_prompt[:200] + "...")

def show_template_usage():
    """Show how to use different template types"""
    print("PROMPT TEMPLATE USAGE EXAMPLES:")
    print("1. Basic: select_prompt_template('basic', ingredients='chicken, rice')")
    print("2. Quick: select_prompt_template('quick', ingredients='pasta, sauce', max_time=20)")
    print("3. Cuisine: select_prompt_template('cuisine', ingredients='beef, spices', cuisine='Mexican')")
    print("4. Dietary: select_prompt_template('dietary', ingredients='tofu, vegetables', dietary_type='vegan')")
    print("5. Substitution: select_prompt_template('substitution', original_recipe='...', missing='eggs', available='applesauce')")

if __name__ == "__main__":
    print("Testing prompt template system...")
    test_prompt_templates()
    print("\n" + "="*70 + "\n")
    show_template_usage()