"""
Migration script to add Phase 2 AI Processing tables
Run this script to create the new tables in your database
"""

import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine, Base
from app.models import (
    ProcessingJob,
    ProcessedContent,
    ChatMessage,
    TextClassification,
    JobType,
    JobStatus,
    ContentType,
    ChatRole,
    ClassificationType,
    Priority
)


def create_phase2_tables():
    """Create Phase 2 tables in the database"""
    print("Creating Phase 2 AI Processing tables...")

    # Import all models to ensure they're registered
    from app import models

    # Create only the new Phase 2 tables
    tables_to_create = [
        ProcessingJob.__table__,
        ProcessedContent.__table__,
        ChatMessage.__table__,
        TextClassification.__table__,
    ]

    print(f"Tables to create: {[t.name for t in tables_to_create]}")

    # Create the tables
    Base.metadata.create_all(bind=engine, tables=tables_to_create)

    print(" Phase 2 tables created successfully!")
    print("\nCreated tables:")
    print("  - processing_jobs")
    print("  - processed_content")
    print("  - chat_messages")
    print("  - text_classifications")


if __name__ == "__main__":
    try:
        create_phase2_tables()
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)
