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
