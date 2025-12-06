import mysql.connector
from mysql.connector import Error


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Ensure __init__ runs only once
        if not hasattr(self, 'initialized'):
            # Configure MySQL connection
            self.config = {
                'host': 'localhost',
                'user': 'root',
                'password': '',  # Empty password (update if needed)
                'database': 'unify',
                'raise_on_warnings': False
            }
            self.initialized = True

    def get_connection(self):
        """
        Returns a NEW connection to MySQL.
        Always close this connection after use (use try/finally or context manager).
        """
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except Error as e:
            print(f"ERROR connecting to MySQL: {e}")
            raise


# Test function - run this file directly to test the connection
if __name__ == "__main__":
    print("Testing MySQL database connection...")
    print("-" * 50)
    
    try:
        db = DatabaseConnection()
        conn = db.get_connection()
        
        if conn:
            print("[OK] Successfully connected to MySQL database 'unify'")
            conn.close()
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
        print("\nMake sure:")
        print("  1. MySQL is running")
        print("  2. Database 'unify' exists (CREATE DATABASE unify;)")
        print("  3. User 'root' exists with empty password")
        print("  3. Server name is correct: DESKTOP-V6DPJFP\\SQLEXPRESS")
        print("  4. ODBC Driver 17 for SQL Server is installed")
        print("\nTo check SQL Server services:")
        print("  - Open Services (services.msc)")
        print("  - Find 'SQL Server (SQLEXPRESS)' and start it")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
