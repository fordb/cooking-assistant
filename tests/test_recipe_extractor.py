"""
Tests for simplified recipe extraction system.
"""

import pytest

from src.core.recipe_extractor import (
    RecipeExtractor, RecipeExtractionResult, 
    get_recipe_extractor, extract_recipe_from_text
)


class TestRecipeExtractor:
    """Test RecipeExtractor class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.extractor = RecipeExtractor()
    
    def test_extract_simple_recipe_success(self):
        """Test extracting a simple recipe."""
        text = """
        Simple Pasta Recipe
        
        - 1 lb pasta
        - 2 cups tomato sauce
        - 1/2 cup parmesan cheese
        
        1. Cook pasta in boiling water for 10 minutes
        2. Heat tomato sauce in a pan
        3. Mix pasta with sauce and serve with cheese
        
        Prep time: 5 minutes
        Cook time: 15 minutes
        Serves: 4
        """
        
        result = self.extractor.extract_recipe(text)
        
        assert result.success is True
        assert result.recipe is not None
        
        recipe = result.recipe
        assert recipe.title == "Simple Pasta Recipe"
        assert len(recipe.ingredients) == 3
        assert len(recipe.instructions) == 3
        assert recipe.prep_time == 5
        assert recipe.cook_time == 15
        assert recipe.servings == 4
    
    def test_extract_recipe_with_override_name(self):
        """Test extraction with name override."""
        text = """
        - 2 cups flour
        - 1 cup sugar
        
        1. Mix ingredients together
        2. Bake for thirty minutes
        3. Cool before serving
        """
        
        result = self.extractor.extract_recipe(text, recipe_name="Custom Cake")
        
        assert result.success is True
        assert result.recipe.title == "Custom Cake"
    
    def test_extract_recipe_minimal_content(self):
        """Test extraction with minimal content using defaults."""
        text = "Short"  # Too short to be a valid title
        
        result = self.extractor.extract_recipe(text)
        
        # Should still succeed with defaults
        assert result.success is True
        recipe = result.recipe
        assert recipe.title == "Extracted Recipe"
        assert len(recipe.ingredients) >= 2  # Uses defaults
        assert len(recipe.instructions) >= 3  # Uses defaults
    
    def test_extract_name_from_first_line(self):
        """Test name extraction from first line."""
        text = "Chocolate Chip Cookies\n\nSome other content"
        name = self.extractor._extract_name(text)
        assert name == "Chocolate Chip Cookies"
    
    def test_extract_bullet_points(self):
        """Test bullet point extraction."""
        text = """
        - First ingredient
        - Second ingredient  
        • Third ingredient
        * Fourth ingredient
        """
        
        items = self.extractor._extract_bullet_points(text)
        
        assert len(items) == 4
        assert "First ingredient" in items
        assert "Third ingredient" in items
    
    def test_extract_numbered_steps(self):
        """Test numbered step extraction."""
        text = """
        1. First step here
        2. Second step here
        3. Third step here
        """
        
        steps = self.extractor._extract_numbered_steps(text)
        
        assert len(steps) == 3
        assert "First step here" in steps
        assert "Third step here" in steps
    
    def test_extract_time_patterns(self):
        """Test time extraction."""
        text = "Prep time: 15 minutes, Cook: 30 min"
        
        prep_time = self.extractor._extract_time(text, "prep")
        cook_time = self.extractor._extract_time(text, "cook")
        
        assert prep_time == 15
        assert cook_time == 30
    
    def test_extract_servings(self):
        """Test servings extraction."""
        text = "Serves 6 people"
        servings = self.extractor._extract_servings(text)
        assert servings == 6


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def setup_method(self):
        """Reset singleton for clean tests."""
        import src.core.recipe_extractor
        src.core.recipe_extractor._extractor = None
    
    def test_extract_recipe_from_text_convenience(self):
        """Test convenience function."""
        text = """
        Salt Water Recipe
        
        - 1 cup water
        - 2 tbsp salt
        
        1. Boil the water carefully
        2. Add salt and stir well
        3. Serve when ready
        """
        
        result = extract_recipe_from_text(text)
        
        assert result.success is True
        assert result.recipe.title == "Salt Water Recipe"
        assert len(result.recipe.ingredients) == 2
    
    def test_singleton_pattern(self):
        """Test singleton pattern works."""
        extractor1 = get_recipe_extractor()
        extractor2 = get_recipe_extractor()
        assert extractor1 is extractor2