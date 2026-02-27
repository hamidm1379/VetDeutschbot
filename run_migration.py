"""
Migration script to add name and mobile columns to users table.
Supports MySQL and MariaDB (set DB_DRIVER=mysql or DB_DRIVER=mariadb in .env).
"""
from db import get_script_connection
from config import Config
import sys


def _placeholder_query(query):
    """Use ? for MariaDB, %s for MySQL."""
    if Config.DB_DRIVER == 'mariadb':
        return query.replace('%s', '?')
    return query


def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    query = """
        SELECT COUNT(*) as count
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s
        AND TABLE_NAME = %s
        AND COLUMN_NAME = %s
    """
    cursor.execute(
        _placeholder_query(query),
        (Config.DB_NAME, table_name, column_name),
    )
    result = cursor.fetchone()
    return result[0] > 0 if result else False


def run_migration():
    """Run migration to add name and mobile columns."""
    try:
        connection, DBError = get_script_connection()
        cursor = connection.cursor()

        print("Checking users table structure...")

        if not column_exists(cursor, 'users', 'name'):
            print("Adding 'name' column to users table...")
            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN name VARCHAR(255) DEFAULT NULL
                COMMENT 'User full name'
                AFTER telegram_id
            """
            )
            connection.commit()
            print("[OK] 'name' column added successfully")
        else:
            print("[SKIP] 'name' column already exists")

        if not column_exists(cursor, 'users', 'mobile'):
            print("Adding 'mobile' column to users table...")
            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN mobile VARCHAR(20) DEFAULT NULL
                COMMENT 'User mobile number'
                AFTER name
            """
            )
            connection.commit()
            print("[OK] 'mobile' column added successfully")
        else:
            print("[SKIP] 'mobile' column already exists")

        cursor.close()
        connection.close()

        print("\n[SUCCESS] Migration completed successfully!")
        return True

    except Exception as e:
        print(f"\n[ERROR] Database error: {e}")
        return False


if __name__ == '__main__':
    print("=" * 50)
    print("Migration: Add name and mobile columns to users table")
    print("=" * 50)
    print()

    if not Config.validate():
        print("[ERROR] Configuration validation failed")
        print("Please check your .env file.")
        sys.exit(1)

    print(f"Database: {Config.DB_NAME}")
    print(f"Host: {Config.DB_HOST}")
    print(f"Driver: {Config.DB_DRIVER}")
    print()

    success = run_migration()

    if not success:
        sys.exit(1)
