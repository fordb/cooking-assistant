import unittest
from src.output_validator import validate_recipe_structure, validate_measurements


class TestOutputValidator(unittest.TestCase):
    def test_validate_recipe_structure_valid(self):
        """Test validation with valid recipe structure"""
        valid_recipe = {
            "title": "Test Recipe",
            "prep_time": 10,
            "cook_time": 20,
            "servings": 4,
            "difficulty": "Beginner",
            "ingredients": ["1 cup flour", "2 eggs", "1 tsp salt"],
            "instructions": ["Mix ingredients", "Cook for 10 minutes", "Serve hot"]
        }
        
        is_valid, errors = validate_recipe_structure(valid_recipe)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_recipe_structure_missing_field(self):
        """Test validation with missing required field"""
        invalid_recipe = {
            "title": "Test Recipe",
            "prep_time": 10,
            # missing cook_time
            "servings": 4,
            "difficulty": "Beginner",
            "ingredients": ["1 cup flour"],
            "instructions": ["Mix ingredients"]
        }
        
        is_valid, errors = validate_recipe_structure(invalid_recipe)
        self.assertFalse(is_valid)
        self.assertIn("cook_time", str(errors))

    def test_validate_recipe_structure_invalid_difficulty(self):
        """Test validation with invalid difficulty"""
        invalid_recipe = {
            "title": "Test Recipe",
            "prep_time": 10,
            "cook_time": 20,
            "servings": 4,
            "difficulty": "Expert",  # Invalid difficulty
            "ingredients": ["1 cup flour"],
            "instructions": ["Mix ingredients"]
        }
        
        is_valid, errors = validate_recipe_structure(invalid_recipe)
        self.assertFalse(is_valid)
        self.assertIn("difficulty", str(errors))

    def test_validate_measurements_valid(self):
        """Test measurement validation with valid measurements"""
        valid_ingredients = [
            "1 cup flour",
            "2 tablespoons sugar",
            "1/2 teaspoon salt",
            "3 large eggs"
        ]
        
        is_valid, errors = validate_measurements(valid_ingredients)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_measurements_missing_amounts(self):
        """Test measurement validation with missing amounts"""
        invalid_ingredients = [
            "flour",  # Missing amount
            "2 tablespoons sugar",
            "salt"    # Missing amount
        ]
        
        is_valid, errors = validate_measurements(invalid_ingredients)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_validate_measurements_mixed_valid_invalid(self):
        """Test measurement validation with mix of valid and invalid"""
        mixed_ingredients = [
            "1 cup flour",      # Valid
            "some sugar",       # Invalid - vague amount
            "2 eggs",          # Valid
            "a pinch of salt"  # Valid - acceptable vague measurement
        ]
        
        is_valid, errors = validate_measurements(mixed_ingredients)
        # Should flag the vague "some sugar" but accept "a pinch"
        self.assertFalse(is_valid)


if __name__ == '__main__':
    unittest.main()