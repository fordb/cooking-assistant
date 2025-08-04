#!/usr/bin/env python3
"""
Demo script showcasing hybrid search functionality combining sparse and dense search.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.vector.store import VectorRecipeStore

def demo_hybrid_search():
    """Demonstrate hybrid search capabilities and advantages."""
    print("🔍 Hybrid Search Demo (BM25 + Semantic)")
    print("=" * 50)
    
    # Initialize vector store
    store = VectorRecipeStore()
    
    # Basic info
    recipe_count = store.count_recipes()
    print(f"📊 Database: {recipe_count} recipes loaded")
    print(f"⚙️  Configuration:")
    print(f"   - Sparse weight: {store.config.HYBRID_SPARSE_WEIGHT}")
    print(f"   - Dense weight: {store.config.HYBRID_DENSE_WEIGHT}")
    print(f"   - RRF K value: {store.config.RRF_K}")
    
    # Test queries that showcase hybrid search advantages
    test_queries = [
        {
            "query": "chicken fried rice",
            "description": "Exact keyword match - sparse search should excel"
        },
        {
            "query": "comfort food for cold weather",
            "description": "Conceptual query - dense search should excel"
        },
        {
            "query": "quick vegetarian dinner",
            "description": "Mixed query - hybrid should combine both strengths"
        },
        {
            "query": "spicy Asian cuisine",
            "description": "Category + attribute - benefits from both approaches"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        description = test_case["description"]
        
        print(f"\n{'='*60}")
        print(f"🔍 Test {i}: '{query}'")
        print(f"💡 Expected: {description}")
        print("=" * 60)
        
        # Get results from all three search methods
        sparse_results = store.search_recipes_sparse(query, n_results=3)
        dense_results = store.search_recipes(query, n_results=3)
        hybrid_results = store.search_recipes_hybrid(query, n_results=3)
        
        # Display sparse search results
        print(f"\n🏷️  SPARSE SEARCH (BM25) - {len(sparse_results)} results:")
        if sparse_results:
            for j, result in enumerate(sparse_results, 1):
                title = result['recipe'].get('title', 'Unknown Recipe')
                score = result['score']
                print(f"   {j}. {title} (BM25: {score:.2f})")
        else:
            print("   No results found")
        
        # Display dense search results
        print(f"\n🧠 DENSE SEARCH (Semantic) - {len(dense_results)} results:")
        if dense_results:
            for j, result in enumerate(dense_results, 1):
                title = result['metadata'].get('title', 'Unknown Recipe')
                similarity = result['similarity']
                print(f"   {j}. {title} (Similarity: {similarity:.3f})")
        else:
            print("   No results found")
        
        # Display hybrid search results
        print(f"\n⚡ HYBRID SEARCH (RRF Combined) - {len(hybrid_results)} results:")
        if hybrid_results:
            for j, result in enumerate(hybrid_results, 1):
                title = result['recipe'].get('title', 'Unknown Recipe')
                combined_score = result['combined_score']
                sparse_score = result['sparse_score']
                dense_score = result['dense_score']
                
                # Create score breakdown string
                score_breakdown = []
                if sparse_score > 0:
                    score_breakdown.append(f"BM25: {sparse_score:.2f}")
                if dense_score > 0:
                    score_breakdown.append(f"Sem: {dense_score:.3f}")
                
                print(f"   {j}. {title}")
                print(f"      🎯 Combined RRF: {combined_score:.4f}")
                print(f"      📊 Sources: {' + '.join(score_breakdown) if score_breakdown else 'N/A'}")
        else:
            print("   No results found")
        
        # Analysis of results
        print(f"\n📈 ANALYSIS:")
        analyze_search_results(sparse_results, dense_results, hybrid_results, query)

def analyze_search_results(sparse_results, dense_results, hybrid_results, query):
    """Analyze and compare search results."""
    
    # Count unique recipes across methods
    sparse_ids = {r['recipe_id'] for r in sparse_results}
    dense_ids = {r['id'] for r in dense_results}
    hybrid_ids = {r['recipe_id'] for r in hybrid_results}
    
    # Find overlaps
    sparse_dense_overlap = sparse_ids & dense_ids
    
    print(f"   • Sparse found: {len(sparse_results)} results")
    print(f"   • Dense found: {len(dense_results)} results") 
    print(f"   • Hybrid combined: {len(hybrid_results)} results")
    print(f"   • Method overlap: {len(sparse_dense_overlap)} recipes found by both")
    
    # Analyze hybrid ranking effectiveness
    if hybrid_results:
        has_both_scores = sum(1 for r in hybrid_results if r['sparse_score'] > 0 and r['dense_score'] > 0)
        sparse_only = sum(1 for r in hybrid_results if r['sparse_score'] > 0 and r['dense_score'] == 0)
        dense_only = sum(1 for r in hybrid_results if r['sparse_score'] == 0 and r['dense_score'] > 0)
        
        print(f"   • Hybrid ranking: {has_both_scores} combined, {sparse_only} sparse-only, {dense_only} dense-only")
        
        if has_both_scores > 0:
            print("   💡 Hybrid successfully leveraged both search methods!")
        elif sparse_only > dense_only:
            print("   💡 Query favored keyword matching (sparse search)")
        elif dense_only > sparse_only:
            print("   💡 Query favored conceptual matching (dense search)")

def compare_search_weights():
    """Demonstrate the effect of different sparse/dense weight configurations."""
    print(f"\n{'='*60}")
    print("⚖️  WEIGHT COMPARISON DEMO")
    print("=" * 60)
    
    store = VectorRecipeStore()
    query = "spicy chicken recipe"
    
    weight_configs = [
        (0.8, 0.2, "Sparse-Heavy (keyword focused)"),
        (0.5, 0.5, "Balanced (equal weighting)"),
        (0.2, 0.8, "Dense-Heavy (semantic focused)")
    ]
    
    print(f"🔍 Query: '{query}'")
    
    for sparse_weight, dense_weight, description in weight_configs:
        print(f"\n📊 {description}")
        print(f"   Weights: Sparse={sparse_weight}, Dense={dense_weight}")
        
        results = store.search_recipes_hybrid(
            query, n_results=3,
            sparse_weight=sparse_weight,
            dense_weight=dense_weight
        )
        
        if results:
            for i, result in enumerate(results, 1):
                title = result['recipe'].get('title', 'Unknown Recipe')
                combined_score = result['combined_score']
                print(f"   {i}. {title} (RRF: {combined_score:.4f})")
        else:
            print("   No results found")

if __name__ == "__main__":
    try:
        demo_hybrid_search()
        compare_search_weights()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("💡 Make sure the vector database is running and populated with recipes")