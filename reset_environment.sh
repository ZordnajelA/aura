#!/bin/bash

echo "🔄 Aura Environment Reset Script"
echo "================================"
echo ""
echo "⚠️  WARNING: This will DELETE ALL DATA!"
echo "   - All users, notes, media files"
echo "   - All database tables and data"
echo "   - All uploaded files"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Reset cancelled."
    exit 1
fi

echo ""
echo "🛑 Step 1: Stopping all services..."
docker-compose down

echo ""
echo "🗑️  Step 2: Removing all volumes (this deletes all data)..."
docker volume rm aura_postgres_data 2>/dev/null || echo "  - postgres_data volume not found (ok)"
docker volume rm aura_redis-data 2>/dev/null || echo "  - redis-data volume not found (ok)"
docker volume rm aura_uploads 2>/dev/null || echo "  - uploads volume not found (ok)"

echo ""
echo "🧹 Step 3: Removing any orphaned containers..."
docker-compose rm -f

echo ""
echo "🏗️  Step 4: Rebuilding images (to get latest code)..."
docker-compose build --no-cache

echo ""
echo "🚀 Step 5: Starting all services..."
docker-compose up -d

echo ""
echo "⏳ Step 6: Waiting for services to be ready..."
sleep 5

echo "  - Waiting for PostgreSQL..."
until docker exec aura-postgres pg_isready -U aura_user > /dev/null 2>&1; do
    echo "    PostgreSQL is starting..."
    sleep 2
done
echo "    ✅ PostgreSQL is ready!"

echo "  - Waiting for Redis..."
until docker exec aura-redis redis-cli ping > /dev/null 2>&1; do
    echo "    Redis is starting..."
    sleep 2
done
echo "    ✅ Redis is ready!"

echo "  - Waiting for Backend..."
sleep 5
until curl -s http://localhost:8000/health > /dev/null 2>&1; do
    echo "    Backend is starting..."
    sleep 2
done
echo "    ✅ Backend is ready!"

echo ""
echo "✅ Environment reset complete!"
echo ""
echo "📋 All tables have been created automatically by SQLAlchemy."
echo ""
echo "🔍 Verify the setup:"
echo "  docker-compose ps"
echo "  docker exec aura-postgres psql -U aura_user -d aura_db -c '\dt'"
echo ""
echo "🌐 Services available at:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  AI Service: http://localhost:8001"
echo ""
echo "📝 Next steps:"
echo "  1. Set GOOGLE_API_KEY in ai-service/.env"
echo "  2. Create a new user account"
echo "  3. Upload a file to test AI processing"
echo ""
