"""
Migration script to add name and mobile columns to users table.
This script safely checks if columns exist before adding them.
"""
import mysql.connector
from config import Config
import sys


def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s
        AND TABLE_NAME = %s
        AND COLUMN_NAME = %s
    """, (Config.DB_NAME, table_name, column_name))
    result = cursor.fetchone()
    return result[0] > 0 if result else False


def run_migration():
    """Run migration to add name and mobile columns."""
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = connection.cursor()
        
        print("Checking users table structure...")
        
        # Check if name column exists
        if not column_exists(cursor, 'users', 'name'):
            print("Adding 'name' column to users table...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN name VARCHAR(255) DEFAULT NULL 
                COMMENT 'User full name' 
                AFTER telegram_id
            """)
            connection.commit()
            print("[OK] 'name' column added successfully")
        else:
            print("[SKIP] 'name' column already exists")
        
        # Check if mobile column exists
        if not column_exists(cursor, 'users', 'mobile'):
            print("Adding 'mobile' column to users table...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN mobile VARCHAR(20) DEFAULT NULL 
                COMMENT 'User mobile number' 
                AFTER name
            """)
            connection.commit()
            print("[OK] 'mobile' column added successfully")
        else:
            print("[SKIP] 'mobile' column already exists")
        
        cursor.close()
        connection.close()
        
        print("\n[SUCCESS] Migration completed successfully!")
        return True
        
    except mysql.connector.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
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
    print()
    
    success = run_migration()
    
    if not success:
        sys.exit(1)
