"""
Test cases for recipe evaluation.

Contains diverse ingredient combinations covering different scenarios,
template types, and complexity levels for comprehensive evaluation.
"""

# Basic template test cases - diverse ingredient combinations
BASIC_TEST_CASES = [
    {"ingredients": "chicken breast, rice, broccoli, soy sauce"},
    {"ingredients": "ground beef, pasta, tomatoes, onion, garlic"},
    {"ingredients": "salmon, potatoes, asparagus, lemon"},
    {"ingredients": "eggs, cheese, spinach, mushrooms"},
    {"ingredients": "tofu, bell peppers, ginger, sesame oil"},
    {"ingredients": "pork chops, apples, sweet potatoes, thyme"},
    {"ingredients": "shrimp, quinoa, avocado, lime, cilantro"},
    {"ingredients": "chicken thighs, carrots, celery, onions"},
]

# Quick meal test cases - under 30 minutes
QUICK_TEST_CASES = [
    {"ingredients": "pasta, olive oil, garlic, parmesan", "template_type": "quick"},
    {"ingredients": "eggs, bread, cheese, butter", "template_type": "quick"},
    {"ingredients": "tuna, white beans, tomatoes, basil", "template_type": "quick"},
    {"ingredients": "chicken strips, vegetables, teriyaki sauce", "template_type": "quick"},
    {"ingredients": "ramen noodles, egg, green onions, soy sauce", "template_type": "quick"},
]

# Dietary restriction test cases
DIETARY_TEST_CASES = [
    {
        "ingredients": "chickpeas, spinach, coconut milk, curry powder",
        "template_type": "dietary", 
        "kwargs": {"dietary_type": "vegan"}
    },
    {
        "ingredients": "chicken, zucchini noodles, pesto, cherry tomatoes",
        "template_type": "dietary",
        "kwargs": {"dietary_type": "keto"}
    },
    {
        "ingredients": "rice flour, eggs, milk, blueberries",
        "template_type": "dietary",
        "kwargs": {"dietary_type": "gluten-free"}
    },
    {
        "ingredients": "lentils, vegetables, vegetable broth, herbs",
        "template_type": "dietary",
        "kwargs": {"dietary_type": "vegetarian"}
    },
]

# Cuisine-specific test cases
CUISINE_TEST_CASES = [
    {
        "ingredients": "ground pork, ginger, soy sauce, rice vinegar",
        "template_type": "cuisine",
        "kwargs": {"cuisine": "Chinese"}
    },
    {
        "ingredients": "tomatoes, mozzarella, basil, olive oil",
        "template_type": "cuisine", 
        "kwargs": {"cuisine": "Italian"}
    },
    {
        "ingredients": "beans, rice, peppers, cumin, lime",
        "template_type": "cuisine",
        "kwargs": {"cuisine": "Mexican"}
    },
    {
        "ingredients": "coconut milk, curry paste, fish sauce, basil",
        "template_type": "cuisine",
        "kwargs": {"cuisine": "Thai"}
    },
    {
        "ingredients": "yogurt, tandoori spice, chicken, basmati rice",
        "template_type": "cuisine",
        "kwargs": {"cuisine": "Indian"}
    },
]

# Substitution test cases
SUBSTITUTION_TEST_CASES = [
    {
        "ingredients": "N/A",  # Not applicable for substitution
        "template_type": "substitution",
        "kwargs": {
            "original_recipe": "Beef Stir Fry with rice, beef, broccoli, soy sauce",
            "missing": "beef",
            "available": "chicken, tofu"
        }
    },
    {
        "ingredients": "N/A",
        "template_type": "substitution", 
        "kwargs": {
            "original_recipe": "Pasta Carbonara with pasta, eggs, bacon, parmesan",
            "missing": "bacon",
            "available": "mushrooms, peas"
        }
    },
]

# Edge cases - challenging ingredient combinations
EDGE_CASE_TEST_CASES = [
    {"ingredients": "bananas, chicken, soy sauce, honey"},  # Unusual combination
    {"ingredients": "chocolate, beans, chili powder, lime"},  # Dessert-savory mix
    {"ingredients": "fish, pineapple, coconut, rice"},  # Tropical combination
    {"ingredients": "beets, goat cheese, walnuts, honey"},  # Fancy combination
    {"ingredients": "leftover rice, kimchi, egg, sesame oil"},  # Leftovers usage
]

# Combine all test cases
ALL_TEST_CASES = (
    BASIC_TEST_CASES + 
    QUICK_TEST_CASES + 
    DIETARY_TEST_CASES + 
    CUISINE_TEST_CASES + 
    SUBSTITUTION_TEST_CASES + 
    EDGE_CASE_TEST_CASES
)

def get_test_cases(category: str = "all") -> list:
    """Get test cases by category."""
    categories = {
        "basic": BASIC_TEST_CASES,
        "quick": QUICK_TEST_CASES,
        "dietary": DIETARY_TEST_CASES,
        "cuisine": CUISINE_TEST_CASES,
        "substitution": SUBSTITUTION_TEST_CASES,
        "edge": EDGE_CASE_TEST_CASES,
        "all": ALL_TEST_CASES
    }
    
    return categories.get(category, ALL_TEST_CASES)

def get_test_case_summary() -> dict:
    """Get summary of test case counts by category."""
    return {
        "basic": len(BASIC_TEST_CASES),
        "quick": len(QUICK_TEST_CASES), 
        "dietary": len(DIETARY_TEST_CASES),
        "cuisine": len(CUISINE_TEST_CASES),
        "substitution": len(SUBSTITUTION_TEST_CASES),
        "edge_cases": len(EDGE_CASE_TEST_CASES),
        "total": len(ALL_TEST_CASES)
    }