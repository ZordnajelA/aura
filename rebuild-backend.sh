#!/bin/bash
# Script to rebuild backend with fresh dependencies

echo "🔄 Rebuilding backend with fixed bcrypt dependency..."

# Stop the backend
echo "⏹️  Stopping backend container..."
docker-compose stop backend

# Remove the old backend image to force a fresh build
echo "🗑️  Removing old backend image..."
docker-compose rm -f backend
docker rmi aura-backend 2>/dev/null || true

# Rebuild the backend image with no cache
echo "🔨 Building fresh backend image (this may take a minute)..."
docker-compose build --no-cache backend

# Start the backend
echo "▶️  Starting backend with new image..."
docker-compose up -d backend

# Wait a moment for startup
echo "⏳ Waiting for backend to start..."
sleep 3

# Show the logs
echo ""
echo "📋 Backend logs (checking for bcrypt errors):"
docker-compose logs --tail=30 backend

echo ""
echo "✅ Backend rebuild complete!"
echo "🔍 Check the logs above for any errors."
echo "   You should NOT see any bcrypt AttributeError messages."
