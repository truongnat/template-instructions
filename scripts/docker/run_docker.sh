#!/bin/bash
echo "🚀 Starting Agentic SDLC via Docker..."

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
  echo "❌ Docker daemon is not running. Please start Docker Desktop/Daemon."
  exit 1
fi

echo "🔄 Building and starting containers..."
docker-compose up -d --build

echo "✅ Services started!"
echo "   - Core App: Shell available (exec into container)"
echo "   - Memgraph Lab: http://localhost:3000"
echo "   - Ollama: http://localhost:11434"
echo ""
echo "To enter the app container:"
echo "   docker-compose exec app bash"
