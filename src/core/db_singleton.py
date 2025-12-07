import pyodbc


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Ensure __init__ runs only once
        if not hasattr(self, 'initialized'):
            # Configure SQL Server connection
            self.connection_string = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=DESKTOP-V6DPJFP\\SQLEXPRESS;"
                "DATABASE=unify;"
                "Trusted_Connection=yes;"
            )
            self.initialized = True

    def get_connection(self):
        """
        Returns a NEW connection to SQL Server.
        Always close this connection after use (use try/finally or context manager).
        """
        try:
            conn = pyodbc.connect(self.connection_string)
            return conn
        except Exception as e:
            print(f"ERROR connecting to SQL Server: {e}")
            raise


# Test function - run this file directly to test the connection
if __name__ == "__main__":
    print("Testing SQL Server database connection...")
    print("-" * 50)
    
    try:
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
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
        print("\nMake sure:")
        print("  1. SQL Server is running")
        print("  2. Database 'unify' exists")
        print("  3. Server name is correct: DESKTOP-V6DPJFP\\SQLEXPRESS")
        print("  4. ODBC Driver 17 for SQL Server is installed")
        print("\nTo check SQL Server services:")
        print("  - Open Services (services.msc)")
        print("  - Find 'SQL Server (SQLEXPRESS)' and start it")
