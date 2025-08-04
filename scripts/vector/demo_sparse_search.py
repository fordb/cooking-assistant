#!/usr/bin/env python3
"""
Demo script showcasing sparse search functionality using BM25.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.vector.store import VectorRecipeStore

def demo_sparse_search():
    """Demonstrate sparse search capabilities using BM25."""
    print("Sparse Search Demo (BM25)")
    
    # Initialize vector store
    store = VectorRecipeStore()
    
    # Basic info
    recipe_count = store.count_recipes()
    print(f"Database: {recipe_count} recipes loaded")
    
    # Test sparse search examples
    print("\nSparse Search Examples:")
    
    queries = [
        "chicken fried rice",
        "vegetable curry spices", 
        "quick pasta dinner",
        "soup comfort food"
    ]
    
    for query in queries:
        print(f"\nSparse search: '{query}'")
        results = store.search_recipes_sparse(query, n_results=3)
        
        if results:
            for i, result in enumerate(results, 1):
                title = result['recipe'].get('title', 'Unknown Recipe')
                score = result['score']
                print(f"  {i}. {title} (BM25 score: {score:.2f})")
        else:
            print("  No results found")

if __name__ == "__main__":
    demo_sparse_search()