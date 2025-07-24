from openai import OpenAI
from config import OPENAI_API_KEY
from src.models import Recipe
from src.examples import load_example_recipes, get_few_shot_examples

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
    print("\n=== Testing Example Recipes ===")
    recipes = load_example_recipes()
    print(f"Loaded {len(recipes)} example recipes:")
    for i, recipe in enumerate(recipes, 1):
        print(f"{i}. {recipe.title} ({recipe.difficulty}, {recipe.prep_time + recipe.cook_time} min)")
    
    print("\n=== Few-Shot Examples Format ===")
    few_shot = get_few_shot_examples(2)
    print(few_shot[:500] + "..." if len(few_shot) > 500 else few_shot)

if __name__ == "__main__":
    test_connection()
    test_model()
    test_examples()