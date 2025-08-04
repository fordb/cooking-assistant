#!/usr/bin/env python3
"""
Demo script showcasing vector database search capabilities.
This script demonstrates how to use the vector database for semantic recipe search.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.vector.store import VectorRecipeStore

def demo_vector_search():
    """Simple demo of vector database semantic search."""
    print("Vector Database Search Demo")
    
    # Initialize vector store
    store = VectorRecipeStore()
    
    # Basic info
    recipe_count = store.count_recipes()
    print(f"Database: {recipe_count} recipes loaded")
    
    # Test semantic search
    if os.getenv('OPENAI_API_KEY'):
        print("\nSemantic Search Examples:")
        
        queries = ["quick chicken meal", "comfort food soup", "vegetarian dinner"]
        
        for query in queries:
            print(f"\nSearching: '{query}'")
            results = store.search_recipes(query, n_results=2)
            
            for i, result in enumerate(results, 1):
                title = result['metadata']['title']
                similarity = result['similarity'] * 100
                print(f"  {i}. {title} ({similarity:.1f}% match)")
    else:
        print("\nSet OPENAI_API_KEY environment variable to enable semantic search")

if __name__ == "__main__":
    demo_vector_search()