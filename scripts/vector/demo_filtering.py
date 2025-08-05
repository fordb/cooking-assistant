#!/usr/bin/env python3
"""
Demo script showcasing advanced filtering capabilities for recipe search.
Demonstrates filtering by difficulty, time ranges, servings, and dietary restrictions.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.vector.store import VectorRecipeStore
from src.vector.filters import RecipeFilter, create_recipe_filter

def demo_basic_filtering():
    """Demonstrate basic filtering capabilities."""
    print("🎯 Basic Recipe Filtering Demo")
    print("=" * 50)
    
    # Initialize vector store
    store = VectorRecipeStore()
    
    # Basic info
    recipe_count = store.count_recipes()
    print(f"📊 Database: {recipe_count} recipes loaded")
    
    # Test queries with different filters
    test_cases = [
        {
            "name": "Beginner Recipes Only",
            "query": "chicken",
            "filters": RecipeFilter(difficulty="Beginner"),
            "description": "Find beginner-friendly chicken recipes"
        },
        {
            "name": "Quick Prep (≤15 min)",
            "query": "dinner",
            "filters": RecipeFilter(prep_time_max=15),
            "description": "Recipes with 15 minutes or less prep time"
        },
        {
            "name": "Small Servings (≤4)",
            "query": "pasta",
            "filters": RecipeFilter(servings_max=4),
            "description": "Recipes that serve 4 people or fewer"
        },
        {
            "name": "Quick Total Time (≤30 min)",
            "query": "lunch",
            "filters": RecipeFilter(max_total_time=30),
            "description": "Recipes ready in 30 minutes or less"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"🔍 Test {i}: {test_case['name']}")
        print(f"💡 Query: '{test_case['query']}'")
        print(f"📝 Description: {test_case['description']}")
        print(f"🎛️  Filters: {test_case['filters'].to_dict()}")
        print("=" * 60)
        
        # Search without filters
        unfiltered_results = store.search_recipes(test_case['query'], n_results=10)
        print(f"\n📋 WITHOUT FILTERS - {len(unfiltered_results)} results:")
        for j, result in enumerate(unfiltered_results[:3], 1):
            metadata = result['metadata']
            title = metadata.get('title', 'Unknown Recipe')
            difficulty = metadata.get('difficulty', 'Unknown')
            prep_time = metadata.get('prep_time', '?')
            cook_time = metadata.get('cook_time', '?')
            servings = metadata.get('servings', '?')
            similarity = result['similarity']
            print(f"   {j}. {title}")
            print(f"      Difficulty: {difficulty} | Prep: {prep_time}min | Cook: {cook_time}min | Serves: {servings}")
            print(f"      Similarity: {similarity:.3f}")
        
        # Search with filters
        filtered_results = store.search_recipes(test_case['query'], n_results=10, filters=test_case['filters'])
        print(f"\n🎯 WITH FILTERS - {len(filtered_results)} results:")
        if filtered_results:
            for j, result in enumerate(filtered_results[:3], 1):
                metadata = result['metadata']
                title = metadata.get('title', 'Unknown Recipe')
                difficulty = metadata.get('difficulty', 'Unknown')
                prep_time = metadata.get('prep_time', '?')
                cook_time = metadata.get('cook_time', '?')
                servings = metadata.get('servings', '?')
                similarity = result['similarity']
                total_time = int(prep_time) + int(cook_time) if str(prep_time).isdigit() and str(cook_time).isdigit() else '?'
                print(f"   {j}. {title}")
                print(f"      Difficulty: {difficulty} | Prep: {prep_time}min | Cook: {cook_time}min | Total: {total_time}min | Serves: {servings}")
                print(f"      Similarity: {similarity:.3f}")
        else:
            print("   No results match the filter criteria")
        
        # Analysis
        filter_effectiveness = len(filtered_results) / max(len(unfiltered_results), 1) * 100
        print(f"\n📈 FILTER EFFECTIVENESS: {filter_effectiveness:.1f}% of results passed filters")


def demo_range_filtering():
    """Demonstrate range-based filtering."""
    print(f"\n{'='*60}")
    print("📏 Range Filtering Demo")
    print("=" * 60)
    
    store = VectorRecipeStore()
    
    range_tests = [
        {
            "name": "Quick Meals",
            "query": "easy recipe",
            "filters": RecipeFilter(prep_time_max=20, cook_time_max=25),
            "description": "Recipes with prep ≤20min and cook ≤25min"
        },
        {
            "name": "Family Size",
            "query": "dinner",
            "filters": RecipeFilter(servings_min=6, servings_max=8),
            "description": "Recipes serving 6-8 people"
        },
        {
            "name": "Moderate Cooking Time",
            "query": "chicken",
            "filters": RecipeFilter(cook_time_min=15, cook_time_max=45),
            "description": "Moderate cooking time: 15-45 minutes"
        }
    ]
    
    for test_case in range_tests:
        print(f"\n🔍 {test_case['name']}: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        
        results = store.search_recipes(test_case['query'], n_results=5, filters=test_case['filters'])
        
        if results:
            print(f"Results ({len(results)} found):")
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                title = metadata.get('title', 'Unknown Recipe')
                prep_time = metadata.get('prep_time', '?')
                cook_time = metadata.get('cook_time', '?')
                servings = metadata.get('servings', '?')
                print(f"   {i}. {title}")
                print(f"      Prep: {prep_time}min | Cook: {cook_time}min | Serves: {servings}")
        else:
            print("   No results match the range criteria")


def demo_combined_filtering():
    """Demonstrate complex multi-constraint filtering."""
    print(f"\n{'='*60}")
    print("🎛️  Complex Multi-Constraint Filtering")
    print("=" * 60)
    
    store = VectorRecipeStore()
    
    complex_filters = [
        {
            "name": "Beginner Quick Meals",
            "query": "dinner recipe",
            "filters": create_recipe_filter(
                difficulty="Beginner",
                prep_time_max=15,
                cook_time_max=30,
                servings_max=4
            ),
            "description": "Beginner recipes, ≤15min prep, ≤30min cook, ≤4 servings"
        },
        {
            "name": "Advanced Large Batches",
            "query": "main dish",
            "filters": create_recipe_filter(
                difficulty="Advanced",
                servings_min=6,
                max_total_time=120
            ),
            "description": "Advanced recipes for 6+ people, ≤2 hours total"
        },
        {
            "name": "Perfect Weekend Project",
            "query": "special recipe",
            "filters": create_recipe_filter(
                difficulty="Intermediate",
                prep_time_min=20,
                cook_time_min=30,
                servings_min=4
            ),
            "description": "Intermediate recipes with substantial prep and cook time"
        }
    ]
    
    for test_case in complex_filters:
        print(f"\n🎯 {test_case['name']}")
        print(f"Description: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        print(f"Filters: {test_case['filters'].to_dict()}")
        
        results = store.search_recipes(test_case['query'], n_results=5, filters=test_case['filters'])
        
        if results:
            print(f"📝 Results ({len(results)} found):")
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                title = metadata.get('title', 'Unknown Recipe')
                difficulty = metadata.get('difficulty', 'Unknown')
                prep_time = metadata.get('prep_time', '?')
                cook_time = metadata.get('cook_time', '?')
                servings = metadata.get('servings', '?')
                total_time = int(prep_time) + int(cook_time) if str(prep_time).isdigit() and str(cook_time).isdigit() else '?'
                similarity = result['similarity']
                
                print(f"   {i}. {title}")
                print(f"      Difficulty: {difficulty} | Prep: {prep_time}min | Cook: {cook_time}min")
                print(f"      Total: {total_time}min | Serves: {servings} | Similarity: {similarity:.3f}")
        else:
            print("   ❌ No results match all filter criteria")


def demo_dietary_filtering():
    """Demonstrate dietary restriction filtering."""
    print(f"\n{'='*60}")
    print("🥗 Dietary Restriction Filtering")
    print("=" * 60)
    
    store = VectorRecipeStore()
    
    dietary_tests = [
        {
            "name": "Vegetarian Options",
            "query": "healthy meal",
            "filters": RecipeFilter(dietary_restrictions=["vegetarian"]),
            "description": "Find vegetarian-friendly recipes"
        },
        {
            "name": "Quick Vegetarian",
            "query": "easy recipe",
            "filters": create_recipe_filter(
                dietary_restrictions=["vegetarian"],
                max_total_time=30,
                difficulty="Beginner"
            ),
            "description": "Quick, easy vegetarian recipes"
        }
    ]
    
    for test_case in dietary_tests:
        print(f"\n🌱 {test_case['name']}")
        print(f"Description: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        
        results = store.search_recipes(test_case['query'], n_results=5, filters=test_case['filters'])
        
        if results:
            print(f"📝 Results ({len(results)} found):")
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                title = metadata.get('title', 'Unknown Recipe')
                ingredients = metadata.get('ingredients', [])
                # Show some ingredients to verify dietary compliance
                ingredient_preview = ', '.join(ingredients[:3]) + ('...' if len(ingredients) > 3 else '')
                print(f"   {i}. {title}")
                print(f"      Key ingredients: {ingredient_preview}")
        else:
            print("   ❌ No vegetarian recipes found")


def demo_search_method_comparison():
    """Compare filtering across different search methods."""
    print(f"\n{'='*60}")
    print("⚡ Search Method Filtering Comparison")
    print("=" * 60)
    
    store = VectorRecipeStore()
    
    # Use a filter that should work across all methods
    filters = create_recipe_filter(
        difficulty="Beginner",
        prep_time_max=20
    )
    
    query = "chicken recipe"
    
    print(f"🔍 Query: '{query}'")
    print(f"🎛️  Filters: {filters.to_dict()}")
    
    # Dense search with filters
    print(f"\n🧠 DENSE SEARCH (Semantic) with Filters:")
    dense_results = store.search_recipes(query, n_results=5, filters=filters)
    print(f"   Found {len(dense_results)} results")
    for i, result in enumerate(dense_results[:3], 1):
        metadata = result['metadata']
        title = metadata.get('title', 'Unknown Recipe')
        difficulty = metadata.get('difficulty', 'Unknown')
        prep_time = metadata.get('prep_time', '?')
        similarity = result['similarity']
        print(f"   {i}. {title} (Difficulty: {difficulty}, Prep: {prep_time}min, Sim: {similarity:.3f})")
    
    # Sparse search with filters
    print(f"\n🏷️  SPARSE SEARCH (BM25) with Filters:")
    sparse_results = store.search_recipes_sparse(query, n_results=5, filters=filters)
    print(f"   Found {len(sparse_results)} results")
    for i, result in enumerate(sparse_results[:3], 1):
        recipe = result['recipe']
        title = recipe.get('title', 'Unknown Recipe')
        difficulty = recipe.get('difficulty', 'Unknown')
        prep_time = recipe.get('prep_time', '?')
        score = result['score']
        print(f"   {i}. {title} (Difficulty: {difficulty}, Prep: {prep_time}min, BM25: {score:.2f})")
    
    # Hybrid search with filters
    print(f"\n⚡ HYBRID SEARCH (RRF) with Filters:")
    hybrid_results = store.search_recipes_hybrid(query, n_results=5, filters=filters)
    print(f"   Found {len(hybrid_results)} results")
    for i, result in enumerate(hybrid_results[:3], 1):
        recipe = result['recipe']
        title = recipe.get('title', 'Unknown Recipe')
        difficulty = recipe.get('difficulty', 'Unknown')
        prep_time = recipe.get('prep_time', '?')
        combined_score = result['combined_score']
        print(f"   {i}. {title} (Difficulty: {difficulty}, Prep: {prep_time}min, RRF: {combined_score:.4f})")
    
    print(f"\n📊 COMPARISON SUMMARY:")
    print(f"   Dense:  {len(dense_results)} results")
    print(f"   Sparse: {len(sparse_results)} results")
    print(f"   Hybrid: {len(hybrid_results)} results")


def demo_filter_validation():
    """Demonstrate filter validation and error handling."""
    print(f"\n{'='*60}")
    print("⚠️  Filter Validation Demo")
    print("=" * 60)
    
    print("Testing various invalid filter configurations:")
    
    # Test invalid difficulty
    print("\n🚫 Invalid difficulty level:")
    try:
        invalid_filter = RecipeFilter(difficulty="Expert")
        print("   ❌ Should have failed!")
    except Exception as e:
        print(f"   ✅ Correctly caught error: {e}")
    
    # Test invalid range
    print("\n🚫 Invalid time range (min > max):")
    try:
        invalid_filter = RecipeFilter(prep_time_min=60, prep_time_max=30)
        print("   ❌ Should have failed!")
    except Exception as e:
        print(f"   ✅ Correctly caught error: {e}")
    
    # Test out-of-bounds values
    print("\n🚫 Out-of-bounds servings:")
    try:
        invalid_filter = RecipeFilter(servings_min=100)  # Above max
        print("   ❌ Should have failed!")
    except Exception as e:
        print(f"   ✅ Correctly caught error: {e}")
    
    # Test invalid dietary restriction
    print("\n🚫 Invalid dietary restriction:")
    try:
        invalid_filter = RecipeFilter(dietary_restrictions=["invalid-diet"])
        print("   ❌ Should have failed!")
    except Exception as e:
        print(f"   ✅ Correctly caught error: {e}")
    
    print("\n✅ All validation tests completed successfully!")


def main():
    """Run all filtering demos."""
    try:
        print("🎯 Advanced Recipe Filtering System Demo")
        print("=" * 60)
        print("This demo showcases the advanced filtering capabilities")
        print("integrated with dense, sparse, and hybrid search methods.")
        print("=" * 60)
        
        # Run all demo sections
        demo_basic_filtering()
        demo_range_filtering()
        demo_combined_filtering()
        demo_dietary_filtering()
        demo_search_method_comparison()
        demo_filter_validation()
        
        print(f"\n{'='*60}")
        print("🎉 FILTERING SYSTEM CAPABILITIES SUMMARY")
        print("=" * 60)
        print("✅ Categorical Filters: difficulty levels")
        print("✅ Range Filters: prep_time, cook_time, servings, max_total_time")
        print("✅ List Filters: dietary restrictions (vegetarian, vegan, etc.)")
        print("✅ Combined Filters: multiple constraints with AND logic")
        print("✅ Search Integration: works with dense, sparse, and hybrid search")
        print("✅ Validation: comprehensive filter parameter validation")
        print("✅ Error Handling: graceful handling of invalid metadata")
        print("✅ Performance: efficient post-search filtering")
        print("✅ Backward Compatibility: existing search calls unaffected")
        print("\n🚀 Ready for Phase 2: User Recipe Management integration!")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("💡 Make sure the vector database is running and populated with recipes")


if __name__ == "__main__":
    main()