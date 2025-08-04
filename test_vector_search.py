#!/usr/bin/env python3
"""
Test script for semantic search queries on the populated vector database.
"""

from src.vector_store import VectorRecipeStore
from src.config import get_config

def test_semantic_searches():
    """Test various semantic search queries."""
    print("=== Testing Vector Database Semantic Search ===\n")
    
    # Initialize vector store
    store = VectorRecipeStore()
    config = get_config()
    
    # Ensure collection exists (it should after population)
    try:
        collection = store.collection
        recipe_count = store.count_recipes()
        print(f"📊 Database Status:")
        print(f"   Collection: {collection.name}")
        print(f"   Total recipes: {recipe_count}")
        print()
    except Exception as e:
        print(f"❌ Failed to access collection: {e}")
        return
    
    # Test queries
    test_queries = [
        {
            "query": "chicken dish",
            "description": "Looking for chicken-based recipes"
        },
        {
            "query": "quick breakfast",
            "description": "Fast morning meal options"
        },
        {
            "query": "vegetarian meals",
            "description": "Plant-based recipe options"
        },
        {
            "query": "Italian pasta",
            "description": "Italian-style pasta dishes"
        },
        {
            "query": "healthy salad",
            "description": "Fresh salad recipes"
        },
        {
            "query": "comfort food soup",
            "description": "Warming soup recipes"
        },
        {
            "query": "spicy Asian stir fry",
            "description": "Asian-style stir-fried dishes"
        },
        {
            "query": "dessert cookies",
            "description": "Sweet cookie recipes"
        }
    ]
    
    # Run test queries
    for i, test in enumerate(test_queries, 1):
        print(f"🔍 Test {i}: {test['description']}")
        print(f"   Query: \"{test['query']}\"")
        
        try:
            results = store.search_recipes(test['query'], n_results=3)
            
            if results:
                print(f"   Results ({len(results)} found):")
                for j, result in enumerate(results, 1):
                    recipe_title = result['metadata']['title']
                    difficulty = result['metadata']['difficulty']
                    similarity = result['similarity']  # Already converted to similarity
                    print(f"     {j}. {recipe_title}")
                    print(f"        Difficulty: {difficulty}")
                    print(f"        Similarity: {similarity:.3f}")
            else:
                print("   No results found")
                
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
        
        print()
    
    # Test similarity threshold
    print("🎯 Testing Similarity Threshold:")
    print("   Query: \"Japanese sushi\" (should find few/no matches)")
    
    try:
        results = store.search_recipes("Japanese sushi", n_results=5)
        if results:
            print(f"   Found {len(results)} results:")
            for result in results:
                similarity = result['similarity']
                print(f"     - {result['metadata']['title']}: {similarity:.3f}")
        else:
            print("   No results found (expected for Japanese sushi)")
    except Exception as e:
        print(f"   ❌ Search failed: {e}")
    
    print("\n✅ Semantic search testing completed!")

if __name__ == "__main__":
    test_semantic_searches()