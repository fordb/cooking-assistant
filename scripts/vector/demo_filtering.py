#!/usr/bin/env python3
"""
Demo script showcasing advanced filtering capabilities for recipe search.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.vector.store import VectorRecipeStore
from src.vector.filters import RecipeFilter

def demo_basic_filtering():
    """Basic filtering examples."""
    print("Basic Filtering Examples")
    print("-" * 25)
    
    store = VectorRecipeStore()
    
    # Difficulty filter
    filters = RecipeFilter(difficulty="Beginner")
    results = store.search_recipes("chicken", n_results=3, filters=filters)
    print(f"\nBeginner chicken recipes: {len(results)} found")
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        print(f"  {i}. {metadata.get('title', 'Unknown')} - {metadata.get('difficulty')}")
    
    # Time filter
    filters = RecipeFilter(prep_time_max=15)
    results = store.search_recipes("dinner", n_results=3, filters=filters)
    print(f"\nQuick prep dinner recipes (≤15min): {len(results)} found")
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        prep_time = metadata.get('prep_time', '?')
        print(f"  {i}. {metadata.get('title', 'Unknown')} - Prep: {prep_time}min")

def demo_range_filtering():
    """Range-based filtering examples."""
    print("\nRange Filtering Examples")
    print("-" * 25)
    
    store = VectorRecipeStore()
    
    # Multiple range constraints
    filters = RecipeFilter(prep_time_max=20, cook_time_max=30, servings_min=4)
    results = store.search_recipes("easy recipe", n_results=3, filters=filters)
    print(f"\nQuick family meals (prep≤20min, cook≤30min, serves≥4): {len(results)} found")
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        prep = metadata.get('prep_time', '?')
        cook = metadata.get('cook_time', '?')
        serves = metadata.get('servings', '?')
        print(f"  {i}. {metadata.get('title', 'Unknown')} - Prep:{prep}min Cook:{cook}min Serves:{serves}")

def demo_combined_filtering():
    """Complex multi-constraint filtering examples."""
    print("\nCombined Filtering Examples")
    print("-" * 27)
    
    store = VectorRecipeStore()
    
    # Complex filter
    filters = RecipeFilter(
        difficulty="Intermediate",
        prep_time_min=15,
        cook_time_max=45,
        servings_min=4
    )
    results = store.search_recipes("main dish", n_results=3, filters=filters)
    print(f"\nIntermediate main dishes (15+min prep, ≤45min cook, 4+ serves): {len(results)} found")
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        diff = metadata.get('difficulty', '?')
        prep = metadata.get('prep_time', '?')
        cook = metadata.get('cook_time', '?')
        serves = metadata.get('servings', '?')
        print(f"  {i}. {metadata.get('title', 'Unknown')} - {diff}, Prep:{prep}min Cook:{cook}min Serves:{serves}")

def demo_search_methods():
    """Compare filtering across search methods."""
    print("\nSearch Method Comparison")
    print("-" * 24)
    
    store = VectorRecipeStore()
    filters = RecipeFilter(difficulty="Beginner", prep_time_max=20)
    query = "chicken recipe"
    
    # Dense search
    dense_results = store.search_recipes(query, n_results=2, filters=filters)
    print(f"\nDense search: {len(dense_results)} results")
    for i, result in enumerate(dense_results, 1):
        metadata = result['metadata']
        print(f"  {i}. {metadata.get('title', 'Unknown')} (sim: {result['similarity']:.3f})")
    
    # Sparse search  
    sparse_results = store.search_recipes_sparse(query, n_results=2, filters=filters)
    print(f"\nSparse search: {len(sparse_results)} results")
    for i, result in enumerate(sparse_results, 1):
        recipe = result['recipe']
        print(f"  {i}. {recipe.get('title', 'Unknown')} (BM25: {result['score']:.2f})")
    
    # Hybrid search
    hybrid_results = store.search_recipes_hybrid(query, n_results=2, filters=filters)
    print(f"\nHybrid search: {len(hybrid_results)} results")
    for i, result in enumerate(hybrid_results, 1):
        recipe = result['recipe']
        print(f"  {i}. {recipe.get('title', 'Unknown')} (RRF: {result['combined_score']:.4f})")

def demo_validation():
    """Filter validation examples."""
    print("\nValidation Examples")
    print("-" * 19)
    
    test_cases = [
        ("Invalid difficulty", lambda: RecipeFilter(difficulty="Expert")),
        ("Invalid range", lambda: RecipeFilter(prep_time_min=60, prep_time_max=30)),
        ("Out of bounds", lambda: RecipeFilter(servings_min=100)),
        ("Invalid dietary", lambda: RecipeFilter(dietary_restrictions=["invalid-diet"]))
    ]
    
    for name, test_func in test_cases:
        try:
            test_func()
            print(f"  ❌ {name}: Should have failed!")
        except Exception as e:
            print(f"  ✅ {name}: Caught error")

def main():
    """Run filtering demos."""
    print("Recipe Filtering System Demo")
    print("=" * 29)
    
    demo_basic_filtering()
    demo_range_filtering() 
    demo_combined_filtering()
    demo_search_methods()
    demo_validation()
    
    print(f"\n{'-'*29}")
    print("Filter capabilities:")
    print("• Difficulty levels")
    print("• Time ranges (prep/cook/total)")
    print("• Serving sizes")
    print("• Dietary restrictions")
    print("• Works with all search methods")

if __name__ == "__main__":
    main()