#!/usr/bin/env python3
"""
Run database migrations
Applies all SQL migrations in db/migrations/ directory
"""
import sqlite3
import os
import sys
from pathlib import Path

DATABASE_PATH = "data/helix_production.db"
MIGRATIONS_DIR = "db/migrations"


def run_migrations():
    """Apply all pending migrations"""
    print("🔄 Running database migrations...")

    # Check if database exists
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ Database not found: {DATABASE_PATH}")
        return False

    # Check if migrations directory exists
    if not os.path.exists(MIGRATIONS_DIR):
        print(f"❌ Migrations directory not found: {MIGRATIONS_DIR}")
        return False

    # Get all .sql files in migrations directory
    migration_files = sorted(Path(MIGRATIONS_DIR).glob("*.sql"))

    if not migration_files:
        print("⚠️  No migration files found")
        return True

    # Apply each migration
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    for migration_file in migration_files:
        print(f"📝 Applying: {migration_file.name}")

        try:
            with open(migration_file, 'r') as f:
                sql = f.read()

            # Execute migration
            cursor.executescript(sql)
            conn.commit()

            print(f"✅ Applied: {migration_file.name}")

        except Exception as e:
            print(f"❌ Error applying {migration_file.name}: {e}")
            conn.rollback()
            return False

    conn.close()

    print("✅ All migrations applied successfully!")
    return True


if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
