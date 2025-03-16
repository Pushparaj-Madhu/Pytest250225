import sqlite3
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

# Database configuration
SQLITE_DB_PATH = 'example.db'
POSTGRES_CONFIG = {
    'dbname': 'your_dbname',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'port': 5432
}

# Connection pool for PostgreSQL
postgres_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **POSTGRES_CONFIG
)

@contextmanager
def sqlite_connection():
    """Context manager for SQLite database connections."""
    conn = None
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        yield conn
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

@contextmanager
def postgres_connection():
    """Context manager for PostgreSQL database connections."""
    conn = None
    try:
        conn = postgres_pool.getconn()
        yield conn
    except psycopg2.Error as e:
        print(f"PostgreSQL error: {e}")
    finally:
        if conn:
            postgres_pool.putconn(conn)

def execute_query(db_type, query, params=None):
    """Execute a query on the specified database."""
    if db_type == 'sqlite':
        with sqlite_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.fetchall()
    elif db_type == 'postgres':
        with postgres_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.fetchall()
    else:
        raise ValueError("Unsupported database type. Use 'sqlite' or 'postgres'.")

# Example usage
if __name__ == "__main__":
    # SQLite example
    sqlite_query = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)"
    execute_query('sqlite', sqlite_query)

    insert_query = "INSERT INTO users (name) VALUES (?)"
    execute_query('sqlite', insert_query, ('Alice',))

    select_query = "SELECT * FROM users"
    rows = execute_query('sqlite', select_query)
    print("SQLite Users:", rows)

    # PostgreSQL example
    postgres_query = "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT)"
    execute_query('postgres', postgres_query)

    insert_query = "INSERT INTO users (name) VALUES (%s)"
    execute_query('postgres', insert_query, ('Bob',))

    select_query = "SELECT * FROM users"
    rows = execute_query('postgres', select_query)
    print("PostgreSQL Users:", rows)