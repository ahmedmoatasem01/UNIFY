"""
Multi-Tenant Database Connection Manager
Manages separate database connections for each user/tenant
"""
import pyodbc
import sqlite3
import os
from threading import Lock

class MultiTenantDatabaseManager:
    """
    Manages database connections for multiple users/tenants.
    Each user can have their own database (SQLite file or separate SQL Server database).
    """
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MultiTenantDatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            # Main/Admin database connection string (for user management)
            self.main_connection_string = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=DESKTOP-V6DPJFP\\SQLEXPRESS;"
                "DATABASE=unify;"
                "Trusted_Connection=yes;"
            )
            
            # Cache for user database connections (user_id -> connection_config)
            self.user_db_configs = {}
            
            # Current user context (thread-local would be better for production)
            self.current_user_id = None
            
            self.initialized = True
    
    def get_main_connection(self):
        """Get connection to main/admin database"""
        try:
            conn = pyodbc.connect(self.main_connection_string)
            return conn
        except Exception as e:
            print(f"ERROR connecting to main database: {e}")
            raise
    
    def set_current_user(self, user_id):
        """Set the current user context"""
        self.current_user_id = user_id
    
    def get_current_user(self):
        """Get the current user context"""
        return self.current_user_id
    
    def load_user_db_config(self, user_id):
        """Load database configuration for a specific user"""
        if user_id in self.user_db_configs:
            return self.user_db_configs[user_id]
        
        # Load from main database
        try:
            conn = self.get_main_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT Config_ID, User_ID, DB_Type, DB_Host, DB_Port, DB_Name, 
                   DB_User, DB_Password, DB_Path, Is_Active
            FROM User_Database_Config
            WHERE User_ID = ? AND Is_Active = 1
            """
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            
            if row:
                config = {
                    'config_id': row[0],
                    'user_id': row[1],
                    'db_type': row[2],
                    'db_host': row[3],
                    'db_port': row[4],
                    'db_name': row[5],
                    'db_user': row[6],
                    'db_password': row[7],
                    'db_path': row[8],
                    'is_active': row[9]
                }
                self.user_db_configs[user_id] = config
                cursor.close()
                conn.close()
                return config
            
            cursor.close()
            conn.close()
            
            # If no config exists, create default SQLite database
            return self._create_default_user_db(user_id)
            
        except Exception as e:
            print(f"Error loading user database config: {e}")
            return self._create_default_user_db(user_id)
    
    def _create_default_user_db(self, user_id):
        """Create default SQLite database configuration for user"""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users')
        os.makedirs(data_dir, exist_ok=True)
        
        db_path = os.path.join(data_dir, f'user_{user_id}.db')
        
        config = {
            'config_id': None,
            'user_id': user_id,
            'db_type': 'sqlite',
            'db_host': None,
            'db_port': None,
            'db_name': None,
            'db_user': None,
            'db_password': None,
            'db_path': db_path,
            'is_active': True
        }
        
        self.user_db_configs[user_id] = config
        return config
    
    def get_user_connection(self, user_id=None):
        """Get database connection for a specific user"""
        if user_id is None:
            user_id = self.current_user_id
        
        if user_id is None:
            # Fallback to main database
            return self.get_main_connection()
        
        config = self.load_user_db_config(user_id)
        
        if config['db_type'] == 'sqlite':
            return self._get_sqlite_connection(config)
        elif config['db_type'] == 'sqlserver':
            return self._get_sqlserver_connection(config)
        elif config['db_type'] == 'mysql':
            return self._get_mysql_connection(config)
        elif config['db_type'] == 'postgresql':
            return self._get_postgresql_connection(config)
        else:
            raise ValueError(f"Unsupported database type: {config['db_type']}")
    
    def _get_sqlite_connection(self, config):
        """Get SQLite connection"""
        try:
            db_path = config['db_path']
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            return conn
        except Exception as e:
            print(f"ERROR connecting to SQLite database: {e}")
            raise
    
    def _get_sqlserver_connection(self, config):
        """Get SQL Server connection"""
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
            print(f"ERROR connecting to SQL Server database: {e}")
            raise
    
    def _get_mysql_connection(self, config):
        """Get MySQL connection (requires mysql-connector-python)"""
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host=config['db_host'],
                port=config['db_port'] or 3306,
                database=config['db_name'],
                user=config['db_user'],
                password=config['db_password']
            )
            return conn
        except ImportError:
            raise ImportError("mysql-connector-python is not installed. Install it with: pip install mysql-connector-python")
        except Exception as e:
            print(f"ERROR connecting to MySQL database: {e}")
            raise
    
    def _get_postgresql_connection(self, config):
        """Get PostgreSQL connection (requires psycopg2)"""
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=config['db_host'],
                port=config['db_port'] or 5432,
                database=config['db_name'],
                user=config['db_user'],
                password=config['db_password']
            )
            return conn
        except ImportError:
            raise ImportError("psycopg2 is not installed. Install it with: pip install psycopg2-binary")
        except Exception as e:
            print(f"ERROR connecting to PostgreSQL database: {e}")
            raise
    
    def execute_query(self, query, params=None, user_id=None):
        """Execute a query on user's database"""
        conn = self.get_user_connection(user_id)
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Check if it's a SELECT query
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                cursor.close()
                conn.close()
                return results
            else:
                conn.commit()
                cursor.close()
                conn.close()
                return True
        except Exception as e:
            print(f"Error executing query: {e}")
            conn.close()
            raise
    
    def fetch_one(self, query, params=None, user_id=None):
        """Fetch one row from user's database"""
        conn = self.get_user_connection(user_id)
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
    
    def fetch_all(self, query, params=None, user_id=None):
        """Fetch all rows from user's database"""
        conn = self.get_user_connection(user_id)
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
    
    def execute_update(self, query, params=None, user_id=None):
        """Execute INSERT/UPDATE/DELETE on user's database"""
        conn = self.get_user_connection(user_id)
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            
            # Get last inserted id if applicable
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
    
    def initialize_user_database(self, user_id, db_type='sqlite', **kwargs):
        """Initialize a new database for a user"""
        if db_type == 'sqlite':
            # Create SQLite database and tables
            config = self._create_default_user_db(user_id)
            conn = self._get_sqlite_connection(config)
            
            # Create standard tables
            self._create_user_tables(conn, db_type='sqlite')
            conn.close()
            
            # Save configuration to main database
            self._save_user_db_config(config)
            
            return config
        
        elif db_type == 'sqlserver':
            # Create configuration for SQL Server
            config = {
                'user_id': user_id,
                'db_type': 'sqlserver',
                'db_host': kwargs.get('db_host'),
                'db_port': kwargs.get('db_port', 1433),
                'db_name': kwargs.get('db_name'),
                'db_user': kwargs.get('db_user'),
                'db_password': kwargs.get('db_password'),
                'db_path': None,
                'is_active': True
            }
            
            self.user_db_configs[user_id] = config
            
            # Save configuration
            self._save_user_db_config(config)
            
            return config
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _create_user_tables(self, conn, db_type='sqlite'):
        """Create standard tables in user's database"""
        cursor = conn.cursor()
        
        # Example: Create tasks table
        if db_type == 'sqlite':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Tasks (
                    Task_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Title TEXT NOT NULL,
                    Description TEXT,
                    Due_Date TIMESTAMP,
                    Priority TEXT,
                    Status TEXT DEFAULT 'pending',
                    Completed INTEGER DEFAULT 0,
                    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Notes (
                    Note_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Title TEXT NOT NULL,
                    Content TEXT,
                    Category TEXT,
                    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    Updated_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Events (
                    Event_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Title TEXT NOT NULL,
                    Description TEXT,
                    Start_Date TIMESTAMP,
                    End_Date TIMESTAMP,
                    Location TEXT,
                    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        conn.commit()
        cursor.close()
    
    def _save_user_db_config(self, config):
        """Save user database configuration to main database"""
        try:
            conn = self.get_main_connection()
            cursor = conn.cursor()
            
            # Check if config already exists
            cursor.execute(
                "SELECT Config_ID FROM User_Database_Config WHERE User_ID = ?",
                (config['user_id'],)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                query = """
                UPDATE User_Database_Config
                SET DB_Type = ?, DB_Host = ?, DB_Port = ?, DB_Name = ?,
                    DB_User = ?, DB_Password = ?, DB_Path = ?, Is_Active = ?
                WHERE User_ID = ?
                """
                cursor.execute(query, (
                    config['db_type'],
                    config['db_host'],
                    config['db_port'],
                    config['db_name'],
                    config['db_user'],
                    config['db_password'],
                    config['db_path'],
                    1 if config['is_active'] else 0,
                    config['user_id']
                ))
            else:
                # Insert new
                query = """
                INSERT INTO User_Database_Config
                (User_ID, DB_Type, DB_Host, DB_Port, DB_Name, DB_User, DB_Password, DB_Path, Is_Active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(query, (
                    config['user_id'],
                    config['db_type'],
                    config['db_host'],
                    config['db_port'],
                    config['db_name'],
                    config['db_user'],
                    config['db_password'],
                    config['db_path'],
                    1 if config['is_active'] else 0
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error saving user database config: {e}")


# Singleton instance
def get_multi_tenant_db():
    """Get the multi-tenant database manager instance"""
    return MultiTenantDatabaseManager()


# Test function
if __name__ == "__main__":
    print("Testing Multi-Tenant Database Manager...")
    print("-" * 50)
    
    try:
        db_manager = get_multi_tenant_db()
        
        # Test main connection
        print("\n1. Testing main database connection...")
        conn = db_manager.get_main_connection()
        if conn:
            print("[OK] Connected to main database")
            conn.close()
        
        # Test user database initialization
        print("\n2. Initializing database for user 1...")
        config = db_manager.initialize_user_database(1, db_type='sqlite')
        print(f"[OK] User database created: {config['db_path']}")
        
        # Test user database connection
        print("\n3. Testing user database connection...")
        db_manager.set_current_user(1)
        conn = db_manager.get_user_connection()
        if conn:
            print("[OK] Connected to user database")
            conn.close()
        
        # Test query execution
        print("\n4. Testing query execution...")
        db_manager.execute_update(
            "INSERT INTO Tasks (Title, Description, Priority) VALUES (?, ?, ?)",
            ("Test Task", "This is a test task", "high"),
            user_id=1
        )
        print("[OK] Inserted test task")
        
        results = db_manager.fetch_all("SELECT * FROM Tasks", user_id=1)
        print(f"[OK] Found {len(results)} tasks")
        
        print("\n" + "=" * 50)
        print("Multi-tenant database system is working!")
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
