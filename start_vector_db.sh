#!/bin/bash

# Start Vector Database Setup Script
# Sets up and starts Chroma DB for the Cooking Assistant

set -e

echo "=== Starting Vector Database Setup ==="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Install Python dependencies if needed
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create data directory for persistence
echo "📁 Creating data directory..."
mkdir -p data/chroma_db

# Start Chroma DB with Docker Compose
echo "🚀 Starting Chroma DB..."
docker-compose up -d chroma

# Wait for Chroma to be ready
echo "⏳ Waiting for Chroma DB to start..."
sleep 5

# Test the connection
echo "🔍 Testing Chroma DB connection..."
python test_chroma_connection.py

if [ $? -eq 0 ]; then
    echo "✅ Vector database setup complete!"
    echo ""
    echo "🎯 Next steps:"
    echo "   - The Chroma DB is now running at http://localhost:8000"
    echo "   - Use 'docker-compose logs chroma' to view logs"
    echo "   - Use 'docker-compose stop chroma' to stop the database"
    echo "   - Use 'docker-compose restart chroma' to restart if needed"
else
    echo "❌ Vector database setup failed!"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   - Check Docker status: docker-compose ps"
    echo "   - View logs: docker-compose logs chroma"
    echo "   - Restart: docker-compose restart chroma"
    exit 1
fi