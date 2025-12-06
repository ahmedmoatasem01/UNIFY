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
            # Configure your SQL Server connection string
            self.connection_string = (
                "DRIVER={ODBC Driver 17 for SQL Server};"  # or "ODBC Driver 18 for SQL Server"
                "SERVER=DESKTOP-V6DPJFP\\SQLEXPRESS;"       # Use your server (e.g., localhost, .\\SQLEXPRESS)
                "DATABASE=unify;"
                "Trusted_Connection=yes;"                   # Windows Authentication (no password)
                # For SQL Server Authentication (username/password), use:
                # "UID=sa;PWD=YourStrongPassword123;"
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
            
            # Test query - show all tables
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
            tables = cursor.fetchall()
            
            print(f"\n[OK] Found {len(tables)} table(s) in the database:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Test database name
            cursor.execute("SELECT DB_NAME()")
            db_name = cursor.fetchone()[0]
            print(f"\n[OK] Connected to database: {db_name}")
            
            # Test a simple query on User table
            try:
                cursor.execute("SELECT COUNT(*) FROM [User]")
                count = cursor.fetchone()[0]
                print(f"[OK] User table is accessible (contains {count} record(s))")
            except Exception as e:
                print(f"[WARNING] User table query failed: {e}")
                print("  (This is okay if the table is empty or doesn't exist yet)")
            
            cursor.close()
            conn.close()
            print("\n" + "-" * 50)
            print("[SUCCESS] Database connection test passed!")
        else:
            print("[ERROR] Failed to connect to database")
            print("Connection object is None")
            
    except pyodbc.Error as e:
        print(f"[ERROR] SQL Server connection error: {e}")
        print("\nPlease check:")
        print("  1. SQL Server is running")
        print("  2. Database 'unify' exists")
        print("  3. Server name is correct: DESKTOP-V6DPJFP\\SQLEXPRESS")
        print("  4. ODBC Driver 17 for SQL Server is installed")
        print("\nTo check SQL Server services:")
        print("  - Open Services (services.msc)")
        print("  - Find 'SQL Server (SQLEXPRESS)' and start it")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
