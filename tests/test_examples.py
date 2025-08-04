import unittest
import json
from src.prompting.examples import load_example_recipes, get_few_shot_examples


class TestExamples(unittest.TestCase):
    def test_load_example_recipes(self):
        """Test loading example recipes from JSON file"""
        recipes = load_example_recipes()
        
        # Should have 15 recipes based on current dataset
        self.assertEqual(len(recipes), 15)
        
        # Each recipe should be a Recipe object
        for recipe in recipes:
            self.assertIsNotNone(recipe.title)
            self.assertIsInstance(recipe.prep_time, int)
            self.assertIsInstance(recipe.cook_time, int)
            self.assertIsInstance(recipe.servings, int)
            self.assertIn(recipe.difficulty, ["Beginner", "Intermediate", "Advanced"])
            self.assertIsInstance(recipe.ingredients, list)
            self.assertIsInstance(recipe.instructions, list)

    def test_get_few_shot_examples_default(self):
        """Test getting few shot examples with default count"""
        examples = get_few_shot_examples()
        
        # Should return string format suitable for prompts
        self.assertIsInstance(examples, str)
        self.assertIn("Recipe", examples)
        self.assertIn("ingredients", examples)
        self.assertIn("instructions", examples)

    def test_get_few_shot_examples_specific_count(self):
        """Test getting specific number of few shot examples"""
        examples = get_few_shot_examples(2)
        
        # Should contain exactly 2 recipes
        recipe_count = examples.count("Example Recipe:")
        self.assertEqual(recipe_count, 2)

    def test_get_few_shot_examples_max_count(self):
        """Test getting more examples than available"""
        examples = get_few_shot_examples(20)  # More than 15 available
        
        # Should return all available recipes
        recipe_count = examples.count("Example Recipe:")
        self.assertEqual(recipe_count, 15)

    def test_get_few_shot_examples_zero_count(self):
        """Test getting zero examples"""
        examples = get_few_shot_examples(0)
        
        # Should return empty string or minimal content
        self.assertIsInstance(examples, str)


if __name__ == '__main__':
    unittest.main()