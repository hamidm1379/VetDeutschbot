"""
Database connection and operations module.
Supports both MySQL (mysql-connector-python) and MariaDB (mariadb).
"""
from contextlib import contextmanager
from config import Config

# Choose driver based on config
if Config.DB_DRIVER == 'mariadb':
    import mariadb
    _using_mariadb = True
else:
    import mysql.connector
    from mysql.connector import pooling
    _using_mariadb = False


def _row_to_dict(cursor, row):
    """Convert a tuple row to dict using cursor description (for MariaDB)."""
    if row is None:
        return None
    if cursor.description:
        return dict(zip([d[0] for d in cursor.description], row))
    return row


class Database:
    """Database connection pool manager (MySQL) or connection manager (MariaDB)."""

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
        if not _using_mariadb:
            self._initialize_mysql_pool()
        # MariaDB: no pool, connection per request

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
        """Get a connection (from pool for MySQL, new for MariaDB)."""
        conn = None
        try:
            if _using_mariadb:
                conn = mariadb.connect(**self.config)
            else:
                conn = self.pool.get_connection()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            err_module = mariadb if _using_mariadb else mysql.connector
            if isinstance(e, (mariadb.Error if _using_mariadb else err_module.Error)):
                print(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _prepare_query(self, query):
        """MariaDB uses ? placeholders; convert %s to ? when using mariadb driver."""
        if _using_mariadb and '%s' in query:
            return query.replace('%s', '?')
        return query

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """Execute a query and optionally return results (rows as dicts)."""
        query = self._prepare_query(query)
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True) if not _using_mariadb else conn.cursor()
            try:
                cursor.execute(query, params or ())
                if fetch_one:
                    row = cursor.fetchone()
                    return _row_to_dict(cursor, row) if _using_mariadb else row
                elif fetch_all:
                    rows = cursor.fetchall()
                    if _using_mariadb and rows and cursor.description:
                        return [_row_to_dict(cursor, r) for r in rows]
                    return rows
                return cursor.lastrowid if cursor.lastrowid else None
            finally:
                cursor.close()

    def execute_many(self, query, params_list):
        """Execute a query multiple times with different parameters."""
        query = self._prepare_query(query)
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
    Uses DB_DRIVER from config (mysql or mariadb).
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
    if Config.DB_DRIVER == 'mariadb':
        return mariadb.connect(**cfg), mariadb.Error
    import mysql.connector
    return mysql.connector.connect(**cfg), mysql.connector.Error
