#!/usr/bin/env python3
"""
Script to populate the vector database with example recipes.
"""

import json
from src.vector.ingestion import RecipeIngestionPipeline
from src.common.config import get_config
from src.recipes.models import Recipe

def main():
    """Populate the vector database with example recipes."""
    print("=== Populating Vector Database with Example Recipes ===\n")
    
    # Load configuration
    config = get_config()
    
    # Initialize ingestion pipeline
    pipeline = RecipeIngestionPipeline()
    
    # Ensure collection exists by accessing it
    print("🔧 Ensuring vector collection exists...")
    try:
        # Try to get existing collection first
        client = pipeline.vector_store.client
        try:
            collection = client.get_collection(config.vector.RECIPE_COLLECTION_NAME)
            print(f"✅ Found existing collection '{collection.name}'")
        except Exception as get_error:
            print(f"📝 Collection doesn't exist ({get_error}), creating new one...")
            collection = client.create_collection(
                name=config.vector.RECIPE_COLLECTION_NAME,
                metadata={
                    "description": "Recipe collection for semantic search",
                    "created_at": "2025-08-04"
                }
            )
            print(f"✅ Created new collection '{collection.name}'")
            
        # Update the internal collection reference
        pipeline.vector_store._collection = collection
        
    except Exception as e:
        print(f"❌ Failed to create/access collection: {e}")
        return
    
    # Load recipes from JSON file
    print("📖 Loading recipes from data/example_recipes.json...")
    with open('data/example_recipes.json', 'r') as f:
        recipe_data = json.load(f)
    
    print(f"✅ Loaded {len(recipe_data)} recipes")
    
    # Convert JSON data to Recipe objects
    print("🔄 Converting to Recipe objects...")
    recipes = []
    for recipe_dict in recipe_data:
        try:
            recipe = Recipe(**recipe_dict)
            recipes.append(recipe)
        except Exception as e:
            print(f"❌ Failed to convert recipe '{recipe_dict.get('title', 'Unknown')}': {e}")
    
    print(f"✅ Converted {len(recipes)} recipes successfully")
    
    # Display recipes being ingested
    print("\n📋 Recipes to be ingested:")
    for i, recipe in enumerate(recipes, 1):
        print(f"  {i:2d}. {recipe.title} ({recipe.difficulty}, {recipe.servings} servings)")
    
    # Ingest recipes into vector database
    print(f"\n🚀 Starting ingestion into collection '{config.vector.RECIPE_COLLECTION_NAME}'...")
    result = pipeline.ingest_recipes(recipes)
    
    # Display results
    stats = result['stats']
    print(f"\n📊 Ingestion Results:")
    print(f"   Status: {result['status']}")
    print(f"   Total recipes processed: {stats['processed']}")
    print(f"   Successfully ingested: {stats['successful']}")
    print(f"   Failed ingestions: {stats['failed']}")
    print(f"   Processing time: {stats.get('duration', 0):.2f} seconds")
    
    if stats['failed'] > 0:
        print(f"\n❌ Some recipes failed to ingest. Check logs for details.")
    else:
        print(f"\n✅ All recipes successfully ingested into vector database!")
    
    # Display collection statistics
    print(f"\n📈 Collection Statistics:")
    recipe_count = pipeline.vector_store.count_recipes()
    print(f"   Collection name: {config.vector.RECIPE_COLLECTION_NAME}")
    print(f"   Total documents: {recipe_count}")
    print(f"   Embedding dimension: {config.vector.EMBEDDING_DIMENSION}")
    
    print(f"\n🎯 Vector database is ready for semantic search!")
    print(f"   - Collection: {config.vector.RECIPE_COLLECTION_NAME}")
    print(f"   - Host: {config.vector.HOST}:{config.vector.PORT}")
    print(f"   - Documents: {recipe_count}")

if __name__ == "__main__":
    main()