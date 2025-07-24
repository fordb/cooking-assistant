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
    few_shot = get_few_shot_examples(5)
    print(few_shot)

if __name__ == "__main__":
    test_connection()
    test_model()
    test_examples()