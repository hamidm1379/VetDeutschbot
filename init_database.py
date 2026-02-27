"""
Database initialization script.
Creates all required tables if they don't exist.
Supports MySQL and MariaDB (set DB_DRIVER=mysql or DB_DRIVER=mariadb in .env).
"""
from db import get_script_connection
from config import Config
import sys


def init_database():
    """Initialize database with required tables."""
    try:
        connection, DBError = get_script_connection(include_database=False)
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
        print("Check MySQL/MariaDB is running and .env credentials.")
        return False
    try:
        cursor = connection.cursor()

        # Create database if it doesn't exist
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.execute(f"USE {Config.DB_NAME}")

        print(f"[OK] Database '{Config.DB_NAME}' ready")

        # Read and execute schema
        print("Reading schema file...")

        try:
            with open('schema_i18n.sql', 'r', encoding='utf-8') as f:
                schema = f.read()
            print("[OK] Using i18n-ready schema (schema_i18n.sql)")
        except FileNotFoundError:
            with open('schema.sql', 'r', encoding='utf-8') as f:
                schema = f.read()
            print("[OK] Using standard schema (schema.sql)")

        # Parse SQL statements: remove comments and split by semicolons
        lines = schema.split('\n')
        cleaned_lines = []
        for line in lines:
            if '--' in line:
                line = line[: line.index('--')]
            cleaned_lines.append(line)

        cleaned_schema = '\n'.join(cleaned_lines)
        statements = [s.strip() for s in cleaned_schema.split(';') if s.strip()]

        print(f"Found {len(statements)} SQL statements to execute")

        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    cursor.execute(statement)
                    connection.commit()
                    first_words = ' '.join(statement.split()[:3])
                    print(f"  [{i}] Executed: {first_words}...")
                except DBError as e:
                    if "already exists" not in str(e).lower():
                        print(f"  Warning [{i}]: {e}")

        print("[OK] Tables created successfully")

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n[OK] Database initialized with {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")

        cursor.close()
        connection.close()
        print("\n[SUCCESS] Database initialization complete!")
        return True
    except DBError as e:
        print(f"\n[ERROR] Database error: {e}")
        print("\nPlease check:")
        print("  1. MySQL/MariaDB server is running")
        print("  2. Database credentials in .env are correct")
        print("  3. User has CREATE DATABASE privileges")
        return False
    finally:
        try:
            cursor.close()
            connection.close()
        except NameError:
            pass


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
    print(f"Driver: {Config.DB_DRIVER}")
    print()

    success = init_database()

    if not success:
        sys.exit(1)
