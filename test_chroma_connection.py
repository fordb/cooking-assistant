#!/usr/bin/env python3
"""
Test script to verify Chroma DB connection and basic functionality.
Run this after starting the Chroma Docker container.
"""

import chromadb
import sys
import time
from src.config import get_vector_config

def test_chroma_connection():
    """Test basic Chroma DB connection and operations."""
    config = get_vector_config()
    
    try:
        print("Testing Chroma DB connection...")
        
        # Connect to Chroma
        chroma_client = chromadb.HttpClient(
            host=config.HOST, 
            port=config.PORT
        )
        
        # Test heartbeat
        print(f"Connecting to Chroma at {config.HOST}:{config.PORT}")
        heartbeat = chroma_client.heartbeat()
        print(f"✅ Heartbeat successful: {heartbeat}")
        
        # List existing collections
        collections = chroma_client.list_collections()
        print(f"✅ Existing collections: {[c.name for c in collections]}")
        
        # Create a test collection
        test_collection_name = "test_cooking_recipes"
        print(f"Creating test collection: {test_collection_name}")
        
        # Delete collection if it exists
        try:
            chroma_client.delete_collection(test_collection_name)
            print(f"Deleted existing test collection")
        except:
            pass
        
        # Create new collection
        test_collection = chroma_client.create_collection(
            name=test_collection_name,
            metadata={"description": "Test collection for cooking recipes"}
        )
        print(f"✅ Created test collection: {test_collection.name}")
        
        # Test basic operations
        test_documents = [
            "Classic Chicken Fried Rice with vegetables and soy sauce",
            "Beef and Broccoli Stir Fry with garlic and ginger",
            "Margherita Pizza with fresh basil and mozzarella"
        ]
        
        test_metadatas = [
            {"title": "Chicken Fried Rice", "difficulty": "Beginner", "cuisine": "Asian"},
            {"title": "Beef and Broccoli", "difficulty": "Beginner", "cuisine": "Asian"},
            {"title": "Margherita Pizza", "difficulty": "Intermediate", "cuisine": "Italian"}
        ]
        
        test_ids = ["recipe_1", "recipe_2", "recipe_3"]
        
        # Add documents
        print("Adding test documents...")
        test_collection.add(
            documents=test_documents,
            metadatas=test_metadatas,
            ids=test_ids
        )
        print(f"✅ Added {len(test_documents)} test documents")
        
        # Query the collection
        print("Testing query functionality...")
        results = test_collection.query(
            query_texts=["chicken rice dish"],
            n_results=2
        )
        
        print(f"✅ Query successful:")
        for i, doc in enumerate(results['documents'][0]):
            distance = results['distances'][0][i]
            metadata = results['metadatas'][0][i]
            print(f"  - {metadata['title']} (distance: {distance:.3f})")
        
        # Clean up
        chroma_client.delete_collection(test_collection_name)
        print(f"✅ Cleaned up test collection")
        
        print("\n🎉 All tests passed! Chroma DB is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Chroma DB: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Docker is running")
        print("2. Start Chroma with: docker-compose up -d chroma")
        print("3. Wait a few seconds for the container to start")
        print("4. Check container status: docker-compose ps")
        return False

def wait_for_chroma(max_attempts=10, delay=3):
    """Wait for Chroma to be available."""
    config = get_vector_config()
    
    for attempt in range(max_attempts):
        try:
            client = chromadb.HttpClient(host=config.HOST, port=config.PORT)
            client.heartbeat()
            print(f"✅ Chroma is ready!")
            return True
        except Exception:
            print(f"Attempt {attempt + 1}/{max_attempts}: Waiting for Chroma to start...")
            time.sleep(delay)
    
    print(f"❌ Chroma not available after {max_attempts} attempts")
    return False

if __name__ == "__main__":
    print("=== Chroma DB Connection Test ===\n")
    
    # Wait for Chroma to be available
    if wait_for_chroma():
        success = test_chroma_connection()
        sys.exit(0 if success else 1)
    else:
        print("Failed to connect to Chroma DB")
        sys.exit(1)