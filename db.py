"""
Database connection and operations module.
Uses mysql-connector-python for async-compatible operations.
"""
import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager
from config import Config


class Database:
    """Database connection pool manager."""
    
    def __init__(self):
        self.config = {
            'host': Config.DB_HOST,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': False,
        }
        self.pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool."""
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="bot_pool",
                pool_size=5,
                pool_reset_session=True,
                **self.config
            )
        except mysql.connector.Error as e:
            print(f"Error creating connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool."""
        try:
            conn = self.pool.get_connection()
            yield conn
            conn.commit()
        except mysql.connector.Error as e:
            if 'conn' in locals():
                conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """Execute a query and optionally return results."""
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
