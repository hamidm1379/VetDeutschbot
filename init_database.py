"""
Database initialization script.
Creates all required tables if they don't exist.
"""
import mysql.connector
from config import Config
import sys


def init_database():
    """Initialize database with required tables."""
    try:
        # Connect to MySQL server (without database first)
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {Config.DB_NAME}")
        
        print(f"[OK] Database '{Config.DB_NAME}' ready")
        
        # Read and execute schema
        print("Reading schema file...")
        
        # Try to use i18n schema first, fallback to regular schema
        try:
            with open('schema_i18n.sql', 'r', encoding='utf-8') as f:
                schema = f.read()
            print("[OK] Using i18n-ready schema (schema_i18n.sql)")
        except FileNotFoundError:
            with open('schema.sql', 'r', encoding='utf-8') as f:
                schema = f.read()
            print("[OK] Using standard schema (schema.sql)")
        
        # Parse SQL statements more carefully
        # Remove comments and split by semicolons
        lines = schema.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove inline comments
            if '--' in line:
                line = line[:line.index('--')]
            cleaned_lines.append(line)
        
        cleaned_schema = '\n'.join(cleaned_lines)
        # Split by semicolons and filter out empty statements
        statements = [s.strip() for s in cleaned_schema.split(';') if s.strip()]
        
        print(f"Found {len(statements)} SQL statements to execute")
        
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    cursor.execute(statement)
                    connection.commit()
                    # Print first few words of statement for debugging
                    first_words = ' '.join(statement.split()[:3])
                    print(f"  [{i}] Executed: {first_words}...")
                except mysql.connector.Error as e:
                    # Ignore "table already exists" errors
                    if "already exists" not in str(e).lower():
                        print(f"  Warning [{i}]: {e}")
        
        print("[OK] Tables created successfully")
        
        # Verify tables exist
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n[OK] Database initialized with {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        connection.close()
        
        print("\n[SUCCESS] Database initialization complete!")
        return True
        
    except mysql.connector.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        print("\nPlease check:")
        print("  1. MySQL server is running")
        print("  2. Database credentials in .env are correct")
        print("  3. User has CREATE DATABASE privileges")
        return False
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return False


if __name__ == '__main__':
    print("=" * 50)
    print("Database Initialization Script")
    print("=" * 50)
    print()
    
    if not Config.validate():
        print("[ERROR] BOT_TOKEN not found in .env file")
        print("Please configure your .env file first.")
        sys.exit(1)
    
    print(f"Connecting to database: {Config.DB_NAME}")
    print(f"Host: {Config.DB_HOST}")
    print(f"User: {Config.DB_USER}")
    print()
    
    success = init_database()
    
    if not success:
        sys.exit(1)
