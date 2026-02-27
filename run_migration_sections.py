"""
Migration script to add sections and lessons tables.
Works with both MySQL and MariaDB (uses mysql-connector-python).
"""
from db import get_script_connection
from config import Config
import sys


def run_migration():
    """Run migration to add sections and lessons tables."""
    try:
        connection, DBError = get_script_connection()
        cursor = connection.cursor()
        
        print(f"[OK] Connected to database: {Config.DB_NAME}")
        print("Reading migration file...")
        
        # Read migration file
        try:
            with open('migration_add_sections_lessons.sql', 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            print("[OK] Migration file loaded")
        except FileNotFoundError:
            print("[ERROR] migration_add_sections_lessons.sql not found!")
            return False
        
        # Parse SQL statements
        lines = migration_sql.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove inline comments
            if '--' in line:
                line = line[:line.index('--')]
            cleaned_lines.append(line)
        
        cleaned_sql = '\n'.join(cleaned_lines)
        # Split by semicolons and filter out empty statements
        statements = [s.strip() for s in cleaned_sql.split(';') if s.strip()]
        
        print(f"Found {len(statements)} SQL statements to execute")
        print()
        
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    cursor.execute(statement)
                    connection.commit()
                    # Print first few words of statement for debugging
                    first_words = ' '.join(statement.split()[:4])
                    print(f"  [{i}] [OK] Executed: {first_words}...")
                except DBError as e:
                    if "already exists" not in str(e).lower():
                        print(f"  [WARNING] [{i}]: {e}")
                    else:
                        print(f"  [{i}] [INFO] Table already exists (skipped)")
        
        print("\n[OK] Migration executed successfully")
        
        # Verify tables exist
        cursor.execute("SHOW TABLES LIKE 'sections'")
        sections_exists = cursor.fetchone()
        cursor.execute("SHOW TABLES LIKE 'lessons'")
        lessons_exists = cursor.fetchone()
        cursor.execute("SHOW TABLES LIKE 'user_section_progress'")
        user_section_progress_exists = cursor.fetchone()
        cursor.execute("SHOW TABLES LIKE 'user_lesson_progress'")
        user_lesson_progress_exists = cursor.fetchone()
        
        print("\n[OK] Verifying tables:")
        if sections_exists:
            print("  [OK] sections table exists")
        else:
            print("  [ERROR] sections table NOT found")
        
        if lessons_exists:
            print("  [OK] lessons table exists")
        else:
            print("  [ERROR] lessons table NOT found")
        
        if user_section_progress_exists:
            print("  [OK] user_section_progress table exists")
        else:
            print("  [ERROR] user_section_progress table NOT found")
        
        if user_lesson_progress_exists:
            print("  [OK] user_lesson_progress table exists")
        else:
            print("  [ERROR] user_lesson_progress table NOT found")
        
        cursor.close()
        connection.close()
        
        print("\n[SUCCESS] Migration complete!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Database error: {e}")
        print("\nPlease check:")
        print("  1. MySQL/MariaDB server is running")
        print("  2. Database credentials in .env are correct")
        print("  3. Database exists and user has privileges")
        return False
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("=" * 50)
    print("Sections & Lessons Migration Script")
    print("=" * 50)
    print()
    
    if not Config.validate():
        print("[ERROR] Configuration not found in .env file")
        print("Please configure your .env file first.")
        sys.exit(1)
    
    print(f"Database: {Config.DB_NAME}")
    print(f"Host: {Config.DB_HOST}")
    print(f"User: {Config.DB_USER}")
    print(f"Driver: {Config.DB_DRIVER}")
    print()
    
    success = run_migration()
    
    if not success:
        sys.exit(1)
    
    print("\n[INFO] Next step: Run 'python init_sections_lessons.py' to create default sections and lessons")
