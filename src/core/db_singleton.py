import pyodbc
import sqlite3
import os

class DatabaseConnection:
    """
    Database Connection Singleton
    Now supports multi-tenant mode where each user can have their own database.
    
    Usage:
    1. For main/admin database: db = DatabaseConnection.get_instance()
    2. For user-specific database: db.set_user_context(user_id)
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Ensure __init__ runs only once
        if not hasattr(self, 'initialized'):
            # Main/Admin SQL Server connection
            self.connection_string = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=DESKTOP-V6DPJFP\\SQLEXPRESS;"
                "DATABASE=unify;"
                "Trusted_Connection=yes;"
            )
            
            # Multi-tenant support
            self.multi_tenant_enabled = os.environ.get('MULTI_TENANT_MODE', 'false').lower() == 'true'
            self.current_user_id = None
            self.user_db_configs = {}
            
            self.initialized = True

    @classmethod
    def get_instance(cls):
        """Get the singleton instance"""
        return cls()
    
    def enable_multi_tenant(self, enabled=True):
        """Enable or disable multi-tenant mode"""
        self.multi_tenant_enabled = enabled
    
    def set_user_context(self, user_id):
        """Set the current user context for multi-tenant mode"""
        self.current_user_id = user_id
    
    def clear_user_context(self):
        """Clear the current user context"""
        self.current_user_id = None

    def get_connection(self):
        """
        Returns a NEW connection to the database.
        In multi-tenant mode, returns user-specific connection.
        Always close this connection after use.
        """
        if self.multi_tenant_enabled and self.current_user_id:
            return self._get_user_connection(self.current_user_id)
        else:
            return self._get_main_connection()
    
    def _get_main_connection(self):
        """Get connection to main/admin database"""
        try:
            conn = pyodbc.connect(self.connection_string)
            return conn
        except Exception as e:
            print(f"ERROR connecting to SQL Server: {e}")
            raise
    
    def _get_user_connection(self, user_id):
        """Get connection to user-specific database"""
        # Load user database configuration
        config = self._load_user_db_config(user_id)
        
        if config['db_type'] == 'sqlite':
            return self._get_sqlite_connection(config)
        elif config['db_type'] == 'sqlserver':
            return self._get_sqlserver_connection(config)
        else:
            # Fallback to main database
            return self._get_main_connection()
    
    def _load_user_db_config(self, user_id):
        """Load database configuration for a user"""
        # Check cache
        if user_id in self.user_db_configs:
            return self.user_db_configs[user_id]
        
        # Load from main database
        try:
            conn = self._get_main_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT DB_Type, DB_Host, DB_Port, DB_Name, DB_User, DB_Password, DB_Path
            FROM User_Database_Config
            WHERE User_ID = ? AND Is_Active = 1
            """
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            
            if row:
                config = {
                    'db_type': row[0],
                    'db_host': row[1],
                    'db_port': row[2],
                    'db_name': row[3],
                    'db_user': row[4],
                    'db_password': row[5],
                    'db_path': row[6]
                }
            else:
                # Create default SQLite config
                config = self._create_default_config(user_id)
            
            cursor.close()
            conn.close()
            
            # Cache it
            self.user_db_configs[user_id] = config
            return config
            
        except Exception as e:
            print(f"Error loading user database config: {e}")
            return self._create_default_config(user_id)
    
    def _create_default_config(self, user_id):
        """Create default SQLite configuration for user"""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users')
        os.makedirs(data_dir, exist_ok=True)
        
        return {
            'db_type': 'sqlite',
            'db_host': None,
            'db_port': None,
            'db_name': None,
            'db_user': None,
            'db_password': None,
            'db_path': os.path.join(data_dir, f'user_{user_id}.db')
        }
    
    def _get_sqlite_connection(self, config):
        """Get SQLite connection"""
        try:
            db_path = config['db_path']
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = sqlite3.connect(db_path)
            return conn
        except Exception as e:
            print(f"ERROR connecting to SQLite database: {e}")
            raise
    
    def _get_sqlserver_connection(self, config):
        """Get SQL Server connection for user database"""
        try:
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={config['db_host']};"
                f"DATABASE={config['db_name']};"
            )
            
            if config['db_user'] and config['db_password']:
                connection_string += f"UID={config['db_user']};PWD={config['db_password']};"
            else:
                connection_string += "Trusted_Connection=yes;"
            
            conn = pyodbc.connect(connection_string)
            return conn
        except Exception as e:
            print(f"ERROR connecting to user SQL Server database: {e}")
            raise
    
    # Helper methods for database operations
    def execute_update(self, query, params=None):
        """Execute INSERT/UPDATE/DELETE query"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            
            # Try to get last insert id
            last_id = None
            try:
                if hasattr(cursor, 'lastrowid'):
                    last_id = cursor.lastrowid
            except:
                pass
            
            cursor.close()
            conn.close()
            return last_id
        except Exception as e:
            print(f"Error executing update: {e}")
            conn.close()
            raise
    
    def fetch_one(self, query, params=None):
        """Fetch one row"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result
        except Exception as e:
            print(f"Error fetching data: {e}")
            conn.close()
            raise
    
    def fetch_all(self, query, params=None):
        """Fetch all rows"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
        except Exception as e:
            print(f"Error fetching data: {e}")
            conn.close()
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