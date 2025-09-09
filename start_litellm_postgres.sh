#!/bin/bash

echo "🐳 Starting PostgreSQL container with Docker..."

# Stop and remove existing container if it exists
docker stop postgres-litellm 2>/dev/null || true
docker rm postgres-litellm 2>/dev/null || true

# Start PostgreSQL container with the credentials from your config
docker run -d \
  --name postgres-litellm \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=postgres \
  -p 5432:5432 \
  postgres:15

echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Check if container is running
if docker ps | grep -q postgres-litellm; then
    echo "✅ PostgreSQL is running successfully!"
    echo "📊 Connection details:"
    echo "   Host: localhost"
    echo "   Port: 5432"
    echo "   Database: postgres"
    echo "   Username: postgres"
    echo "   Password: password"
    echo ""
    echo "🚀 Now starting LiteLLM server..."
    
    # Start LiteLLM server
    if [ -f "litellm_config.yaml" ]; then
        litellm --config litellm_config.yaml
    else
        echo "❌ litellm_config.yaml not found. Please make sure the config file exists."
        echo "Current directory contents:"
        ls -la
    fi
else
    echo "❌ Failed to start PostgreSQL container"
    docker logs postgres-litellm
fi