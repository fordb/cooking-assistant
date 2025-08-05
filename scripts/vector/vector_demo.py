#!/usr/bin/env python3
"""
Comprehensive vector database demo showcasing all search and management capabilities.
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.vector.store import VectorRecipeStore
from src.vector.filters import RecipeFilter
from src.vector.user_collections import UserRecipeCollection, UserRecipeCollectionError
from src.recipes.models import Recipe
from src.common.config import get_logger

logger = get_logger(__name__)


def check_setup():
    """Check if vector database is set up and ready."""
    print("Vector Database Demo")
    print("=" * 30)
    
    store = VectorRecipeStore()
    recipe_count = store.count_recipes()
    
    print(f"Database: {recipe_count} recipes loaded")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  Warning: OPENAI_API_KEY not set. Some features will be limited.")
    
    print()
    return store, api_key, recipe_count > 0


def demo_basic_search(store, has_api_key):
    """Demonstrate basic semantic search capabilities."""
    print("1. SEMANTIC SEARCH")
    print("-" * 20)
    
    if not has_api_key:
        print("Skipping semantic search (requires OPENAI_API_KEY)")
        return
    
    queries = ["quick chicken meal", "comfort food soup", "vegetarian dinner"]
    
    for query in queries:
        print(f"Query: '{query}'")
        results = store.search_recipes(query, n_results=2)
        
        if results:
            for i, result in enumerate(results, 1):
                title = result['metadata']['title']
                similarity = result['similarity'] * 100
                print(f"  {i}. {title} ({similarity:.1f}% match)")
        else:
            print("  No results found")
        print()


def demo_sparse_search(store):
    """Demonstrate sparse/BM25 search capabilities."""
    print("2. SPARSE SEARCH (BM25)")
    print("-" * 25)
    
    queries = ["chicken fried rice", "vegetable curry spices", "quick pasta dinner"]
    
    for query in queries:
        print(f"Query: '{query}'")
        results = store.search_recipes_sparse(query, n_results=2)
        
        if results:
            for i, result in enumerate(results, 1):
                title = result['recipe'].get('title', 'Unknown Recipe')
                score = result['score']
                print(f"  {i}. {title} (BM25: {score:.2f})")
        else:
            print("  No results found")
        print()


def demo_hybrid_search(store, has_api_key):
    """Demonstrate hybrid search combining sparse and dense."""
    print("3. HYBRID SEARCH (RRF)")
    print("-" * 23)
    
    if not has_api_key:
        print("Skipping hybrid search (requires OPENAI_API_KEY)")
        return
    
    queries = ["chicken fried rice", "comfort food for cold weather"]
    
    for query in queries:
        print(f"Query: '{query}'")
        results = store.search_recipes_hybrid(query, n_results=2)
        
        if results:
            for i, result in enumerate(results, 1):
                title = result['recipe'].get('title', 'Unknown Recipe')
                combined_score = result['combined_score']
                sparse_score = result['sparse_score']
                dense_score = result['dense_score']
                
                print(f"  {i}. {title}")
                print(f"     RRF: {combined_score:.4f} (BM25: {sparse_score:.2f}, Semantic: {dense_score:.3f})")
        else:
            print("  No results found")
        print()


def demo_filtering(store, has_api_key):
    """Demonstrate advanced filtering capabilities."""
    print("4. ADVANCED FILTERING")
    print("-" * 22)
    
    # Basic difficulty filter
    filters = RecipeFilter(difficulty="Beginner")
    search_func = store.search_recipes if has_api_key else store.search_recipes_sparse
    query = "chicken" if has_api_key else "chicken recipe"
    
    results = search_func(query, n_results=2, filters=filters)
    print(f"Beginner chicken recipes: {len(results)} found")
    for i, result in enumerate(results, 1):
        if has_api_key:
            metadata = result['metadata']
            title = metadata.get('title', 'Unknown')
            difficulty = metadata.get('difficulty')
        else:
            recipe = result['recipe'] 
            title = recipe.get('title', 'Unknown')
            difficulty = recipe.get('difficulty')
        print(f"  {i}. {title} - {difficulty}")
    print()
    
    # Time range filter
    filters = RecipeFilter(prep_time_max=15, cook_time_max=30)
    results = search_func("dinner", n_results=2, filters=filters)
    print(f"Quick dinner recipes (≤15min prep, ≤30min cook): {len(results)} found")
    for i, result in enumerate(results, 1):
        if has_api_key:
            metadata = result['metadata']
            title = metadata.get('title', 'Unknown')
            prep = metadata.get('prep_time', '?')
            cook = metadata.get('cook_time', '?')
        else:
            recipe = result['recipe']
            title = recipe.get('title', 'Unknown')
            prep = recipe.get('prep_time', '?')
            cook = recipe.get('cook_time', '?')
        print(f"  {i}. {title} - Prep: {prep}min, Cook: {cook}min")
    print()
    
    # Combined constraints
    filters = RecipeFilter(difficulty="Intermediate", servings_min=4, prep_time_max=20)
    results = search_func("main dish", n_results=2, filters=filters)
    print(f"Intermediate family meals (≤20min prep, 4+ servings): {len(results)} found")
    for i, result in enumerate(results, 1):
        if has_api_key:
            metadata = result['metadata']
            title = metadata.get('title', 'Unknown')
            serves = metadata.get('servings', '?')
        else:
            recipe = result['recipe']
            title = recipe.get('title', 'Unknown')
            serves = recipe.get('servings', '?')
        print(f"  {i}. {title} - Serves: {serves}")
    print()


def demo_user_collections(has_api_key):
    """Demonstrate user recipe collections."""
    print("5. USER RECIPE COLLECTIONS")
    print("-" * 27)
    
    if not has_api_key:
        print("User collections require OPENAI_API_KEY for full functionality")
        print("Demo will show structure only")
        print()
    
    try:
        user_id = "demo_user_123"
        user_collection = UserRecipeCollection(user_id, api_key=has_api_key)
        
        print(f"User: {user_id}")
        
        # Create sample recipe
        sample_recipe = Recipe(
            title="Demo Chocolate Chip Cookies",
            ingredients=[
                "2 cups flour",
                "1 cup butter, softened", 
                "3/4 cup brown sugar",
                "2 eggs",
                "2 cups chocolate chips"
            ],
            instructions=[
                "Preheat oven to 375°F",
                "Mix butter and sugar until creamy",
                "Beat in eggs",
                "Mix in flour gradually",
                "Stir in chocolate chips",
                "Bake 9-11 minutes"
            ],
            prep_time=15,
            cook_time=10,
            servings=24,
            difficulty="Beginner"
        )
        
        # Add recipe
        print("Adding sample recipe...")
        try:
            recipe_id = user_collection.add_user_recipe(sample_recipe)
            print(f"✅ Recipe added with ID: {recipe_id}")
        except Exception as e:
            print(f"❌ Failed to add recipe: {e}")
            return
        
        # Get user recipes
        user_recipes = user_collection.get_user_recipes()
        print(f"User has {len(user_recipes)} recipes")
        
        # Search user recipes
        if has_api_key and user_recipes:
            print("Searching user recipes for 'cookies'...")
            try:
                results = user_collection.search_user_recipes("cookies", n_results=2)
                for i, result in enumerate(results, 1):
                    title = result.get('metadata', {}).get('title', 'Unknown')
                    similarity = result.get('similarity', 0)
                    print(f"  {i}. {title} (similarity: {similarity:.3f})")
            except Exception as e:
                print(f"Search failed: {e}")
        
        print()
        
    except UserRecipeCollectionError as e:
        print(f"User collection error: {e}")
    except Exception as e:
        print(f"Demo error: {e}")
        logger.exception("User collections demo failed")


def run_comparison_demo(store, has_api_key):
    """Compare all search methods on the same query."""
    print("6. SEARCH METHOD COMPARISON")
    print("-" * 30)
    
    query = "chicken recipe"
    print(f"Comparing search methods for: '{query}'")
    print()
    
    # Sparse search
    sparse_results = store.search_recipes_sparse(query, n_results=2)
    print(f"Sparse (BM25): {len(sparse_results)} results")
    for i, result in enumerate(sparse_results, 1):
        title = result['recipe'].get('title', 'Unknown')
        score = result['score']
        print(f"  {i}. {title} (BM25: {score:.2f})")
    print()
    
    # Dense search
    if has_api_key:
        dense_results = store.search_recipes(query, n_results=2)
        print(f"Dense (Semantic): {len(dense_results)} results")
        for i, result in enumerate(dense_results, 1):
            title = result['metadata'].get('title', 'Unknown')
            similarity = result['similarity']
            print(f"  {i}. {title} (Similarity: {similarity:.3f})")
        print()
        
        # Hybrid search
        hybrid_results = store.search_recipes_hybrid(query, n_results=2)
        print(f"Hybrid (RRF): {len(hybrid_results)} results")
        for i, result in enumerate(hybrid_results, 1):
            title = result['recipe'].get('title', 'Unknown')
            combined = result['combined_score']
            print(f"  {i}. {title} (RRF: {combined:.4f})")
        print()
    else:
        print("Dense and Hybrid search require OPENAI_API_KEY")
        print()


def main():
    """Run the comprehensive vector database demo."""
    parser = argparse.ArgumentParser(description="Vector Database Demo")
    parser.add_argument('--section', type=int, choices=range(1, 7), 
                       help="Run specific section only (1-6)")
    parser.add_argument('--list-sections', action='store_true',
                       help="List available demo sections")
    
    args = parser.parse_args()
    
    if args.list_sections:
        print("Available demo sections:")
        print("1. Semantic Search")
        print("2. Sparse Search (BM25)")
        print("3. Hybrid Search (RRF)")
        print("4. Advanced Filtering")
        print("5. User Recipe Collections")
        print("6. Search Method Comparison")
        return
    
    try:
        store, api_key, has_recipes = check_setup()
        
        if not has_recipes:
            print("No recipes found in database. Run populate_db.py first.")
            return
        
        sections = {
            1: lambda: demo_basic_search(store, api_key),
            2: lambda: demo_sparse_search(store),
            3: lambda: demo_hybrid_search(store, api_key),
            4: lambda: demo_filtering(store, api_key),
            5: lambda: demo_user_collections(api_key),
            6: lambda: run_comparison_demo(store, api_key)
        }
        
        if args.section:
            sections[args.section]()
        else:
            # Run all sections
            for section_num in sorted(sections.keys()):
                sections[section_num]()
        
        print("Demo completed!")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Demo failed: {e}")
        logger.exception("Vector demo failed")


if __name__ == "__main__":
    main()