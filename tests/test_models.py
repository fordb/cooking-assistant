import unittest
from src.models import Recipe


class TestRecipe(unittest.TestCase):
    def setUp(self):
        self.valid_recipe_data = {
            "title": "Test Recipe",
            "prep_time": 10,
            "cook_time": 20,
            "servings": 2,
            "difficulty": "Beginner",
            "ingredients": ["1 cup rice", "2 cups water"],
            "instructions": ["Cook rice in water", "Serve hot"]
        }

    def test_recipe_creation_valid(self):
        """Test creating a recipe with valid data"""
        recipe = Recipe(**self.valid_recipe_data)
        self.assertEqual(recipe.title, "Test Recipe")
        self.assertEqual(recipe.prep_time, 10)
        self.assertEqual(recipe.cook_time, 20)
        self.assertEqual(recipe.servings, 2)
        self.assertEqual(recipe.difficulty, "Beginner")
        self.assertEqual(len(recipe.ingredients), 2)
        self.assertEqual(len(recipe.instructions), 2)

    def test_recipe_total_time(self):
        """Test total time calculation"""
        recipe = Recipe(**self.valid_recipe_data)
        self.assertEqual(recipe.total_time, 30)

    def test_recipe_invalid_difficulty(self):
        """Test recipe creation with invalid difficulty"""
        invalid_data = self.valid_recipe_data.copy()
        invalid_data["difficulty"] = "Expert"
        
        with self.assertRaises(ValueError):
            Recipe(**invalid_data)

    def test_recipe_negative_times(self):
        """Test recipe creation with negative times"""
        invalid_data = self.valid_recipe_data.copy()
        invalid_data["prep_time"] = -5
        
        with self.assertRaises(ValueError):
            Recipe(**invalid_data)

    def test_recipe_empty_ingredients(self):
        """Test recipe creation with empty ingredients"""
        invalid_data = self.valid_recipe_data.copy()
        invalid_data["ingredients"] = []
        
        with self.assertRaises(ValueError):
            Recipe(**invalid_data)

    def test_recipe_empty_instructions(self):
        """Test recipe creation with empty instructions"""
        invalid_data = self.valid_recipe_data.copy()
        invalid_data["instructions"] = []
        
        with self.assertRaises(ValueError):
            Recipe(**invalid_data)


if __name__ == '__main__':
    unittest.main()