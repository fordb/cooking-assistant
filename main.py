from openai import OpenAI
from config import OPENAI_API_KEY
from src.models import Recipe

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

if __name__ == "__main__":
    test_connection()
    test_model()