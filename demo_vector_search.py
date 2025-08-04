#!/usr/bin/env python3
"""
Demo script showcasing vector database search capabilities.
This script demonstrates how to use the vector database for semantic recipe search.
"""

from src.vector_store import VectorRecipeStore
from src.config import get_config
import os

def demo_vector_search():
    """Demonstrate vector database search capabilities."""
    print("🍳 Vector Database Recipe Search Demo")
    print("=" * 50)
    print()
    
    # Initialize vector store
    store = VectorRecipeStore()
    config = get_config()
    
    # Check if API key is available
    api_key_available = bool(os.getenv('OPENAI_API_KEY'))
    
    # Show database status
    try:
        collection = store.collection
        recipe_count = store.count_recipes()
        
        print(f"📊 Database Status:")
        print(f"   Collection: {collection.name}")
        print(f"   Total recipes: {recipe_count}")
        print(f"   Embedding model: text-embedding-ada-002")
        print(f"   OpenAI API key: {'✅ Available' if api_key_available else '❌ Not configured'}")
        print()
        
    except Exception as e:
        print(f"❌ Failed to access vector database: {e}")
        return
    
    # Show sample recipes in database
    print("📋 Sample Recipes in Database:")
    try:
        # Get a few sample recipes
        all_data = collection.get(limit=5)
        if all_data and 'metadatas' in all_data:
            for i, metadata in enumerate(all_data['metadatas'], 1):
                title = metadata.get('title', 'Unknown')
                difficulty = metadata.get('difficulty', 'Unknown')
                time_info = f"{metadata.get('prep_time', '?')}+{metadata.get('cook_time', '?')}min"
                print(f"   {i}. {title} ({difficulty}, {time_info})")
            print(f"   ... and {recipe_count - 5} more recipes")
        print()
    except Exception as e:
        print(f"   Error retrieving sample recipes: {e}")
        print()
    
    if api_key_available:
        # Demonstrate semantic search with real queries
        print("🔍 Semantic Search Demonstrations:")
        print("   (Using OpenAI embeddings for semantic similarity)")
        print()
        
        demo_queries = [
            {
                "query": "quick chicken meal",
                "description": "Fast chicken-based recipes"
            },
            {
                "query": "comfort food soup",
                "description": "Warming, comforting soup recipes"
            },
            {
                "query": "vegetarian dinner",
                "description": "Plant-based evening meals"
            }
        ]
        
        for i, demo in enumerate(demo_queries, 1):
            print(f"Demo {i}: {demo['description']}")
            print(f"   Query: \"{demo['query']}\"")
            
            try:
                results = store.search_recipes(demo['query'], n_results=3)
                
                if results:
                    print(f"   Top {len(results)} matches:")
                    for j, result in enumerate(results, 1):
                        title = result['metadata']['title']
                        similarity = result['similarity'] * 100  # Convert to percentage
                        print(f"     {j}. {title} ({similarity:.1f}% match)")
                else:
                    print("   No matches found")
                    
            except Exception as e:
                print(f"   ❌ Search failed: {e}")
            
            print()
    
    else:
        # Show how to set up API key and what semantic search would provide
        print("🔑 OpenAI API Key Required for Semantic Search:")
        print("   To enable semantic search capabilities, set your OpenAI API key:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print()
        print("💡 What Semantic Search Provides:")
        print("   • Find recipes by cooking style: 'comfort food', 'healthy meals'")
        print("   • Search by cuisine: 'Italian pasta', 'Asian stir fry'")  
        print("   • Discover by ingredients: 'chicken and rice', 'vegetables'")
        print("   • Query by occasion: 'quick breakfast', 'dinner party'")
        print("   • Match difficulty: 'easy weeknight meal', 'advanced techniques'")
        print()
    
    # Show basic database queries (no API key needed)
    print("📊 Database Query Capabilities (No API Key Required):")
    print("   • Count total recipes")
    print("   • Browse all stored recipes")
    print("   • View recipe metadata and content")
    print("   • Inspect vector embeddings")
    print()
    
    print("🚀 Next Steps for RAG Implementation:")
    print("   1. ✅ Vector database populated with 15 example recipes")
    print("   2. ✅ Semantic search infrastructure ready")
    print("   3. 🔄 Ready to integrate with conversation system")
    print("   4. 🔄 Add context-aware recipe recommendations")
    print("   5. 🔄 Build retrieval-augmented generation pipeline")
    print()
    
    print("📖 Usage Examples:")
    print("   # Basic verification")
    print("   python verify_vector_db.py")
    print()
    print("   # Populate database")
    print("   python populate_vector_db.py")
    print()
    print("   # Search recipes (requires API key)")
    print("   python test_vector_search.py")
    print()
    
    if api_key_available:
        print("✅ Vector database is fully operational for semantic search!")
    else:
        print("🔧 Vector database populated, semantic search ready when API key is configured")

if __name__ == "__main__":
    demo_vector_search()