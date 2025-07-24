import unittest
import warnings
from src.models import Recipe
from src.exceptions import RecipeValidationError


class TestRecipeValidation(unittest.TestCase):
    def test_recipe_creation_valid(self):
        """Test creating a valid recipe"""
        valid_recipe_data = {
            "title": "Test Recipe",
            "prep_time": 10,
            "cook_time": 20,
            "servings": 4,
            "difficulty": "Beginner",
            "ingredients": ["1 cup flour", "2 eggs", "1 tsp salt"],
            "instructions": ["Mix ingredients", "Cook for 10 minutes", "Serve hot"]
        }
        
        recipe = Recipe(**valid_recipe_data)
        self.assertEqual(recipe.title, "Test Recipe")
        self.assertEqual(recipe.total_time, 30)

    def test_recipe_validation_missing_field(self):
        """Test validation with missing required field"""
        invalid_recipe = {
            "title": "Test Recipe",
            "prep_time": 10,
            # missing cook_time
            "servings": 4,
            "difficulty": "Beginner",
            "ingredients": ["1 cup flour", "2 eggs"],
            "instructions": ["Mix ingredients", "Cook", "Serve"]
        }
        
        with self.assertRaises(Exception):  # Pydantic will raise validation error
            Recipe(**invalid_recipe)

    def test_recipe_validation_invalid_difficulty(self):
        """Test validation with invalid difficulty"""
        invalid_recipe = {
            "title": "Test Recipe",
            "prep_time": 10,
            "cook_time": 20,
            "servings": 4,
            "difficulty": "Expert",  # Invalid difficulty
            "ingredients": ["1 cup flour", "2 eggs"],
            "instructions": ["Mix ingredients", "Cook", "Serve"]
        }
        
        with self.assertRaises(RecipeValidationError):
            Recipe(**invalid_recipe)

    def test_recipe_validation_insufficient_ingredients(self):
        """Test validation with insufficient ingredients"""
        invalid_recipe = {
            "title": "Test Recipe",
            "prep_time": 10,
            "cook_time": 20,
            "servings": 4,
            "difficulty": "Beginner",
            "ingredients": ["1 cup flour"],  # Only 1 ingredient
            "instructions": ["Mix ingredients", "Cook", "Serve"]
        }
        
        with self.assertRaises(RecipeValidationError):
            Recipe(**invalid_recipe)

    def test_recipe_validation_insufficient_instructions(self):
        """Test validation with insufficient instructions"""
        invalid_recipe = {
            "title": "Test Recipe",
            "prep_time": 10,
            "cook_time": 20,
            "servings": 4,
            "difficulty": "Beginner",
            "ingredients": ["1 cup flour", "2 eggs"],
            "instructions": ["Mix ingredients", "Cook"]  # Only 2 instructions
        }
        
        with self.assertRaises(RecipeValidationError):
            Recipe(**invalid_recipe)

    def test_recipe_measurement_warnings(self):
        """Test measurement validation warnings"""
        recipe_with_missing_measurements = {
            "title": "Test Recipe",
            "prep_time": 10,
            "cook_time": 20,
            "servings": 4,
            "difficulty": "Beginner",
            "ingredients": ["flour", "2 eggs"],  # First ingredient missing measurement
            "instructions": ["Mix ingredients", "Cook for 10 minutes", "Serve hot"]
        }
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            recipe = Recipe(**recipe_with_missing_measurements)
            self.assertGreater(len(w), 0)
            self.assertIn("measurement", str(w[0].message))


if __name__ == '__main__':
    unittest.main()