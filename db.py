"""
Database connection and operations module.
Uses mysql-connector-python for both MySQL and MariaDB servers (no system C library required).
"""
from contextlib import contextmanager
import mysql.connector
from mysql.connector import pooling

from config import Config


class Database:
    """Database connection pool manager (MySQL and MariaDB compatible)."""

    def __init__(self):
        self.config = {
            'host': Config.DB_HOST,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME,
            'charset': 'utf8mb4',
            'autocommit': False,
        }
        self.pool = None
        self._initialize_mysql_pool()

    def _initialize_mysql_pool(self):
        """Initialize MySQL connection pool."""
        try:
            pool_config = {**self.config, 'collation': 'utf8mb4_unicode_ci'}
            self.pool = pooling.MySQLConnectionPool(
                pool_name="bot_pool",
                pool_size=5,
                pool_reset_session=True,
                **pool_config
            )
        except mysql.connector.Error as e:
            print(f"Error creating connection pool: {e}")
            raise
        self._ensure_tables()

    def _ensure_tables(self):
        """Create all required tables if they do not exist (so bot works without running init_database.py)."""
        tables_sql = [
            """CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                name VARCHAR(255) DEFAULT NULL,
                mobile VARCHAR(20) DEFAULT NULL,
                language VARCHAR(10) DEFAULT NULL,
                current_step INT DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                account_expires_at DATETIME DEFAULT NULL,
                INDEX idx_telegram_id (telegram_id),
                INDEX idx_current_step (current_step)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
            """CREATE TABLE IF NOT EXISTS steps (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title_json JSON NOT NULL,
                description_json JSON DEFAULT NULL,
                file_id VARCHAR(255) DEFAULT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_is_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
            """CREATE TABLE IF NOT EXISTS exams (
                id INT AUTO_INCREMENT PRIMARY KEY,
                step_id INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (step_id) REFERENCES steps(id) ON DELETE CASCADE,
                UNIQUE KEY unique_step_exam (step_id),
                INDEX idx_step_id (step_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
            """CREATE TABLE IF NOT EXISTS questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                exam_id INT NOT NULL,
                question_json JSON NOT NULL,
                options_json TEXT NOT NULL,
                correct_option INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
                INDEX idx_exam_id (exam_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
            """CREATE TABLE IF NOT EXISTS user_exam_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                step_id INT NOT NULL,
                score DECIMAL(5,2) NOT NULL,
                passed BOOLEAN NOT NULL DEFAULT FALSE,
                completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (step_id) REFERENCES steps(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_step_result (user_id, step_id),
                INDEX idx_user_id (user_id),
                INDEX idx_step_id (step_id),
                INDEX idx_passed (passed)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
        ]
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    for sql in tables_sql:
                        cursor.execute(sql)
                finally:
                    cursor.close()
        except mysql.connector.Error as e:
            print(f"Warning: could not ensure tables: {e}")

    @contextmanager
    def get_connection(self):
        """Get a connection from the pool."""
        conn = None
        try:
            conn = self.pool.get_connection()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            if isinstance(e, mysql.connector.Error):
                print(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """Execute a query and optionally return results (rows as dicts)."""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                return cursor.lastrowid if cursor.lastrowid else None
            finally:
                cursor.close()

    def execute_many(self, query, params_list):
        """Execute a query multiple times with different parameters."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany(query, params_list)
                return cursor.rowcount
            finally:
                cursor.close()


# Global database instance
db = Database()


def get_script_connection(include_database=True):
    """
    Return (connection, ErrorClass) for init/migration scripts.
    Works with both MySQL and MariaDB servers.
    Set include_database=False for init_database (connect before DB exists).
    """
    cfg = {
        'host': Config.DB_HOST,
        'user': Config.DB_USER,
        'password': Config.DB_PASSWORD,
        'charset': 'utf8mb4',
    }
    if include_database:
        cfg['database'] = Config.DB_NAME
    return mysql.connector.connect(**cfg), mysql.connector.Error
