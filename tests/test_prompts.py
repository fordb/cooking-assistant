import unittest
from src.prompting.prompts import (
    create_basic_recipe_prompt,
    create_quick_meal_prompt,
    create_dietary_prompt,
    create_cuisine_prompt,
    create_substitution_prompt,
    select_prompt_template,
    TEMPLATE_TYPES
)
from src.common.exceptions import TemplateError


class TestPrompts(unittest.TestCase):
    def test_create_basic_recipe_prompt(self):
        """Test basic recipe prompt creation"""
        ingredients = "chicken, rice, vegetables"
        prompt = create_basic_recipe_prompt(ingredients)
        
        self.assertIsInstance(prompt, str)
        self.assertIn(ingredients, prompt)
        self.assertIn("Chef Marcus", prompt)
        self.assertIn("JSON", prompt)
        self.assertIn("Example Recipe:", prompt)

    def test_create_quick_meal_prompt(self):
        """Test quick meal prompt creation"""
        ingredients = "pasta, sauce"
        max_time = 20
        prompt = create_quick_meal_prompt(ingredients, max_time)
        
        self.assertIsInstance(prompt, str)
        self.assertIn(ingredients, prompt)
        self.assertIn(str(max_time), prompt)
        self.assertIn("quick", prompt.lower())
        self.assertIn("efficiency", prompt)

    def test_create_quick_meal_prompt_default_time(self):
        """Test quick meal prompt with default time"""
        ingredients = "eggs, bread"
        prompt = create_quick_meal_prompt(ingredients)
        
        self.assertIn("30 minutes", prompt)

    def test_create_dietary_prompt(self):
        """Test dietary restriction prompt creation"""
        ingredients = "tofu, vegetables"
        dietary_type = "vegan"
        prompt = create_dietary_prompt(ingredients, dietary_type)
        
        self.assertIsInstance(prompt, str)
        self.assertIn(ingredients, prompt)
        self.assertIn(dietary_type, prompt)
        self.assertIn("DIETARY REQUIREMENTS", prompt)
        self.assertIn("compliance", prompt)

    def test_create_cuisine_prompt(self):
        """Test cuisine-specific prompt creation"""
        ingredients = "beef, spices"
        cuisine = "Mexican"
        prompt = create_cuisine_prompt(ingredients, cuisine)
        
        self.assertIsInstance(prompt, str)
        self.assertIn(ingredients, prompt)
        self.assertIn(cuisine, prompt)
        self.assertIn("CUISINE REQUIREMENTS", prompt)
        self.assertIn("authentic", prompt)

    def test_create_substitution_prompt(self):
        """Test ingredient substitution prompt creation"""
        original_recipe = "Chocolate chip cookies with eggs and butter"
        missing = "eggs"
        available = "applesauce"
        prompt = create_substitution_prompt(original_recipe, missing, available)
        
        self.assertIsInstance(prompt, str)
        self.assertIn(original_recipe, prompt)
        self.assertIn(missing, prompt)
        self.assertIn(available, prompt)
        self.assertIn("substituting", prompt)

    def test_select_prompt_template_basic(self):
        """Test template selection for basic recipe"""
        ingredients = "chicken, rice"
        prompt = select_prompt_template("basic", ingredients=ingredients)
        
        self.assertIsInstance(prompt, str)
        self.assertIn(ingredients, prompt)
        self.assertIn("Chef Marcus", prompt)

    def test_select_prompt_template_quick(self):
        """Test template selection for quick meals"""
        ingredients = "pasta, sauce"
        max_time = 25
        prompt = select_prompt_template("quick", ingredients=ingredients, max_time=max_time)
        
        self.assertIn(ingredients, prompt)
        self.assertIn(str(max_time), prompt)

    def test_select_prompt_template_dietary(self):
        """Test template selection for dietary restrictions"""
        ingredients = "vegetables, quinoa"
        dietary_type = "gluten-free"
        prompt = select_prompt_template("dietary", ingredients=ingredients, dietary_type=dietary_type)
        
        self.assertIn(ingredients, prompt)
        self.assertIn(dietary_type, prompt)

    def test_select_prompt_template_cuisine(self):
        """Test template selection for cuisine types"""
        ingredients = "noodles, soy sauce"
        cuisine = "Chinese"
        prompt = select_prompt_template("cuisine", ingredients=ingredients, cuisine=cuisine)
        
        self.assertIn(ingredients, prompt)
        self.assertIn(cuisine, prompt)

    def test_select_prompt_template_substitution(self):
        """Test template selection for substitutions"""
        original_recipe = "Pancakes with milk and eggs"
        missing = "milk"
        available = "almond milk"
        prompt = select_prompt_template(
            "substitution", 
            original_recipe=original_recipe, 
            missing=missing, 
            available=available
        )
        
        self.assertIn(original_recipe, prompt)
        self.assertIn(missing, prompt)
        self.assertIn(available, prompt)

    def test_select_prompt_template_invalid_type(self):
        """Test template selection with invalid type"""
        with self.assertRaises(TemplateError) as context:
            select_prompt_template("invalid_type", ingredients="test")
        
        self.assertIn("Unknown template type", str(context.exception))

    def test_template_types_constant(self):
        """Test TEMPLATE_TYPES constant structure"""
        self.assertIsInstance(TEMPLATE_TYPES, dict)
        self.assertIn("basic", TEMPLATE_TYPES)
        self.assertIn("quick", TEMPLATE_TYPES)
        self.assertIn("dietary", TEMPLATE_TYPES)
        self.assertIn("cuisine", TEMPLATE_TYPES)
        self.assertIn("substitution", TEMPLATE_TYPES)
        
        # Verify all values are strings
        for template_type, description in TEMPLATE_TYPES.items():
            self.assertIsInstance(template_type, str)
            self.assertIsInstance(description, str)

    def test_select_prompt_template_missing_kwargs(self):
        """Test template selection with missing required kwargs"""
        # Basic template missing ingredients
        with self.assertRaises(TemplateError):
            select_prompt_template("basic")
        
        # Dietary template missing dietary_type
        with self.assertRaises(TemplateError):
            select_prompt_template("dietary", ingredients="test")
        
        # Cuisine template missing cuisine
        with self.assertRaises(TemplateError):
            select_prompt_template("cuisine", ingredients="test")

    def test_prompt_contains_examples(self):
        """Test that prompts contain few-shot examples"""
        prompt = create_basic_recipe_prompt("test ingredients")
        
        # Should contain example recipe format
        self.assertIn("Example Recipe:", prompt)
        self.assertIn("title", prompt)
        self.assertIn("ingredients", prompt)
        self.assertIn("instructions", prompt)


if __name__ == '__main__':
    unittest.main()