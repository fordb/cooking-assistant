from openai import OpenAI
from config import OPENAI_API_KEY
from src.prompts import create_basic_recipe_prompt
from src.models import Recipe
import json

def generate_basic_recipe(ingredients: str) -> Recipe:
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = create_basic_recipe_prompt(ingredients)
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    recipe_json = response.choices[0].message.content
    recipe_data = json.loads(recipe_json)
    return Recipe(**recipe_data)