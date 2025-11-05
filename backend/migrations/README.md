# Database Migrations

This directory contains database migration scripts for Aura.

## Phase 2: AI Processing Tables

The Phase 2 migration adds tables for AI processing functionality:
- `processing_jobs` - Track async AI processing jobs
- `processed_content` - Store AI processing results
- `chat_messages` - Chat interface message history
- `text_classifications` - Content classification results

### Option 1: Run Python Migration Script

From the backend directory:

```bash
cd /home/user/aura/backend
python migrations/add_phase2_tables.py
```

This script will:
- Connect to your database using the config from `.env`
- Create only the new Phase 2 tables
- Skip tables that already exist

### Option 2: Run SQL Script Directly

If you prefer to run SQL directly:

```bash
# Using psql
psql -U aura_user -d aura_db -f migrations/add_phase2_tables.sql

# Or using docker exec
docker exec -i aura-postgres psql -U aura_user -d aura_db < migrations/add_phase2_tables.sql
```

### Option 3: Docker Compose

If you're running with Docker Compose and need to recreate the database:

```bash
# Stop services
docker-compose down

# Remove the database volume (WARNING: This deletes all data!)
docker volume rm aura_postgres_data

# Start services (database will be recreated with all tables)
docker-compose up -d
```

The backend's `init_db()` function will automatically create all tables on startup if they don't exist.

### Verifying Migration

After running the migration, verify the tables exist:

```sql
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('processing_jobs', 'processed_content', 'chat_messages', 'text_classifications');
```

You should see all 4 tables listed.

### Troubleshooting

**Error: "column does not exist"**
- The tables haven't been created yet
- Run one of the migration options above

**Error: "table already exists"**
- The migration has already been run
- Both scripts are idempotent and can be run multiple times safely

**Error: "cannot connect to database"**
- Check your database is running: `docker ps | grep postgres`
- Verify your `.env` file has correct database credentials
- Check `DATABASE_URL` in backend configuration
