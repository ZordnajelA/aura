#!/bin/bash

echo "🔍 Phase 2 Processing Test"
echo "=========================="
echo ""

# 1. Check AI Service
echo "1️⃣ Checking AI Service..."
curl -s http://localhost:8001/health | jq '.' 2>/dev/null || echo "❌ AI Service not responding"
echo ""

# 2. Check latest upload
echo "2️⃣ Latest uploaded file:"
docker exec -it aura-postgres psql -U aura_user -d aura_db -c "
SELECT 
    id,
    file_type,
    is_processed,
    created_at
FROM media 
ORDER BY created_at DESC 
LIMIT 1;
"
echo ""

# 3. Check processing jobs
echo "3️⃣ Processing jobs:"
docker exec -it aura-postgres psql -U aura_user -d aura_db -c "
SELECT 
    id,
    job_type,
    status,
    progress,
    error_message
FROM processing_jobs 
ORDER BY created_at DESC 
LIMIT 3;
"
echo ""

# 4. Check processed results
echo "4️⃣ Processing results:"
docker exec -it aura-postgres psql -U aura_user -d aura_db -c "
SELECT 
    content_type,
    LENGTH(raw_text) as text_length,
    LEFT(summary, 100) as summary_preview,
    confidence_score
FROM processed_content 
ORDER BY created_at DESC 
LIMIT 1;
"
echo ""

echo "✅ Test complete!"
echo ""
echo "To manually process a file:"
echo "  1. Get media_id from the output above"
echo "  2. Run: curl -X POST http://localhost:8000/api/processing/start/{media_id}"
