#!/usr/bin/env python3
"""
Demo script for user recipe collections functionality.
Shows how to upload, validate, and search user-specific recipes.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.vector.user_collections import UserRecipeCollection, UserRecipeCollectionError
from src.recipes.models import Recipe
from src.common.config import get_logger

logger = get_logger(__name__)


def main():
    """Demonstrate user recipe collections functionality."""
    print("=== User Recipe Collections Demo ===\n")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Warning: OPENAI_API_KEY not found. Some features may not work.")
        print("   Demo will continue with mock operations.\n")
    
    try:
        # Initialize user collection
        user_id = "demo_user_123"
        print(f"🏠 Initializing user collection for: {user_id}")
        user_collection = UserRecipeCollection(user_id, api_key=api_key)
        
        # Display initial stats
        stats = user_collection.stats
        print(f"📊 Collection stats:")
        print(f"   - Collection name: {stats['collection_name']}")
        print(f"   - Recipe count: {stats['recipe_count']}")
        print(f"   - Collection exists: {stats['collection_exists']}")
        print(f"   - Max recipes allowed: {stats['max_recipes']}\n")
        
        # Create a sample user recipe
        print("📝 Creating sample user recipe...")
        user_recipe = Recipe(
            title="My Famous Chocolate Chip Cookies",
            ingredients=[
                "2 cups all-purpose flour",
                "1 cup butter, softened",
                "3/4 cup brown sugar",
                "1/2 cup white sugar",
                "2 large eggs",
                "2 tsp vanilla extract",
                "1 tsp baking soda",
                "1 tsp salt",
                "2 cups chocolate chips"
            ],
            instructions=[
                "Preheat oven to 375°F (190°C)",
                "Mix butter, brown sugar, and white sugar until creamy",
                "Beat in eggs and vanilla extract",
                "In separate bowl, combine flour, baking soda, and salt",
                "Gradually mix dry ingredients into wet ingredients",
                "Stir in chocolate chips",
                "Drop rounded tablespoons of dough onto ungreased baking sheets",
                "Bake 9-11 minutes until golden brown",
                "Cool on baking sheets for 2 minutes, then transfer to wire rack"
            ],
            prep_time=15,
            cook_time=10,
            servings=24,
            difficulty="Beginner"
        )
        
        # Add recipe to user collection
        print("📤 Adding recipe to user collection...")
        try:
            recipe_id = user_collection.add_user_recipe(user_recipe)
            print(f"✅ Recipe added successfully with ID: {recipe_id}\n")
        except Exception as e:
            print(f"❌ Failed to add recipe: {e}")
            return
        
        # Create another sample recipe
        print("📝 Creating second sample recipe...")
        user_recipe2 = Recipe(
            title="Quick Veggie Stir Fry",
            ingredients=[
                "2 cups mixed vegetables (bell peppers, broccoli, carrots)",
                "2 tbsp vegetable oil",
                "2 cloves garlic, minced",
                "1 tbsp soy sauce",
                "1 tsp sesame oil",
                "1/4 cup green onions, chopped"
            ],
            instructions=[
                "Heat vegetable oil in large skillet over high heat",
                "Add garlic and stir-fry for 30 seconds",
                "Add mixed vegetables and stir-fry for 3-4 minutes",
                "Add soy sauce and sesame oil, toss to combine",
                "Garnish with green onions and serve immediately"
            ],
            prep_time=10,
            cook_time=5,
            servings=2,
            difficulty="Beginner"
        )
        
        print("📤 Adding second recipe...")
        try:
            recipe_id2 = user_collection.add_user_recipe(user_recipe2)
            print(f"✅ Second recipe added with ID: {recipe_id2}\n")
        except Exception as e:
            print(f"❌ Failed to add second recipe: {e}")
            return
        
        # Get all user recipes
        print("📚 Retrieving all user recipes...")
        user_recipes = user_collection.get_user_recipes()
        print(f"Found {len(user_recipes)} recipes:")
        for recipe in user_recipes:
            metadata = recipe.get('metadata', {})
            print(f"   - {metadata.get('title', 'Unknown')}")
            print(f"     Difficulty: {metadata.get('difficulty', 'Unknown')}")
            print(f"     Time: {metadata.get('prep_time', 0)} prep + {metadata.get('cook_time', 0)} cook mins")
            print(f"     Uploaded: {metadata.get('uploaded_at', 'Unknown')[:19]}")
        print()
        
        # Search user recipes
        if api_key:
            print("🔍 Searching user recipes...")
            search_queries = ["cookies", "quick meal", "vegetarian"]
            
            for query in search_queries:
                print(f"   Query: '{query}'")
                try:
                    results = user_collection.search_user_recipes(query, n_results=5)
                    if results:
                        for result in results:
                            similarity = result.get('similarity', result.get('distance', 0))
                            title = result.get('metadata', {}).get('title', 'Unknown')
                            print(f"     - {title} (similarity: {similarity:.3f})")
                    else:
                        print("     No results found")
                except Exception as e:
                    print(f"     Search failed: {e}")
                print()
        else:
            print("🔍 Skipping search demo (no API key)\n")
        
        # Final stats
        final_stats = user_collection.stats
        print("📊 Final collection stats:")
        print(f"   - Recipe count: {final_stats['recipe_count']}")
        print(f"   - Collection exists: {final_stats['collection_exists']}")
        
        print("\n✅ User recipe collections demo completed!")
        
    except UserRecipeCollectionError as e:
        print(f"❌ User collection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.exception("Demo failed")


if __name__ == "__main__":
    main()