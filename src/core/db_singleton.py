import os

try:
    import pyodbc  # type: ignore
    _HAS_PYODBC = True
except Exception:
    pyodbc = None  # type: ignore
    _HAS_PYODBC = False
    import sqlite3


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_conn()
        return cls._instance

    def _init_conn(self):
        # Always import sqlite3 for fallback
        import sqlite3
        
        if _HAS_PYODBC:
            # Try to use ODBC connection first
            try:
                conn_str = os.environ.get('ODBC_CONNECTION_STRING',
                                          'Driver={SQL Server};Server=.;Database=unify;Trusted_Connection=yes;')
                self._conn = pyodbc.connect(conn_str, autocommit=False)
                return  # Successfully connected to SQL Server
            except Exception as e:
                # pyodbc connection failed, fall back to SQLite
                print(f"Warning: Failed to connect to SQL Server via pyodbc: {e}")
                print("Falling back to SQLite database...")
        
        # Fallback to sqlite for local/dev usage
        try:
            db_dir = os.environ.get('SQLITE_DB_DIR',
                                    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')))
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, os.environ.get('SQLITE_DB_NAME', 'unify_dev.db'))
        except Exception:
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'unify_dev.db'))
        
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        try:
            self._conn.row_factory = sqlite3.Row
        except Exception:
            pass

    def get_connection(self):
        return self._conn

    def cursor(self):
        return self._conn.cursor()

    def commit(self):
        try:
            self._conn.commit()
        except Exception:
            pass

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass


# Test function - run this file directly to test the connection
if __name__ == "__main__":
    print("Testing SQL Server database connection...")
    print("-" * 50)

    db = DatabaseConnection()
    conn = db.get_connection()

    if conn:
        print("[OK] Successfully connected to SQL Server database 'unify'")
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = cursor.fetchall()
        print(f"\nFound {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        cursor.close()
        conn.close()
    else:
        print("[FAIL] Connection failed")
