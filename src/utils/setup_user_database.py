"""
User Database Setup Utility
Initialize individual databases for users
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.multi_tenant_db import MultiTenantDatabaseManager
from core.db_singleton import DatabaseConnection


def setup_user_database_table():
    """Create the User_Database_Config table in main database"""
    print("Setting up User_Database_Config table...")
    
    try:
        db = DatabaseConnection.get_instance()
        conn = db._get_main_connection()
        cursor = conn.cursor()
        
        # Create table
        query = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'User_Database_Config')
        BEGIN
            CREATE TABLE User_Database_Config (
                Config_ID INT PRIMARY KEY IDENTITY(1,1),
                User_ID INT NOT NULL UNIQUE,
                DB_Type NVARCHAR(50) NOT NULL DEFAULT 'sqlite',
                DB_Host NVARCHAR(255),
                DB_Port INT,
                DB_Name NVARCHAR(255),
                DB_User NVARCHAR(255),
                DB_Password NVARCHAR(255),
                DB_Path NVARCHAR(500),
                Is_Active BIT DEFAULT 1,
                Created_Date DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (User_ID) REFERENCES Users(User_ID)
            )
        END
        """
        
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✓ User_Database_Config table created successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error creating table: {e}")
        return False


def initialize_user_database(user_id, db_type='sqlite', **kwargs):
    """Initialize database for a specific user"""
    print(f"\nInitializing database for User ID: {user_id}")
    print(f"Database Type: {db_type}")
    
    try:
        db_manager = MultiTenantDatabaseManager()
        
        # Initialize database
        config = db_manager.initialize_user_database(user_id, db_type, **kwargs)
        
        print(f"✓ Database initialized successfully")
        
        if db_type == 'sqlite':
            print(f"  Database Path: {config['db_path']}")
        else:
            print(f"  Database: {config['db_name']}")
            print(f"  Host: {config['db_host']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False


def initialize_all_users():
    """Initialize databases for all existing users"""
    print("\nInitializing databases for all users...")
    
    try:
        db = DatabaseConnection.get_instance()
        conn = db._get_main_connection()
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute("SELECT User_ID, Username FROM Users")
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        print(f"Found {len(users)} users")
        
        success_count = 0
        for user in users:
            user_id = user[0]
            username = user[1]
            
            print(f"\n[{user_id}] {username}")
            if initialize_user_database(user_id, db_type='sqlite'):
                success_count += 1
        
        print(f"\n" + "="*60)
        print(f"Initialized {success_count}/{len(users)} user databases")
        
        return success_count == len(users)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_user_database(user_id):
    """Test connection to user's database"""
    print(f"\nTesting database for User ID: {user_id}")
    
    try:
        db_manager = MultiTenantDatabaseManager()
        
        # Set user context
        db_manager.set_current_user(user_id)
        
        # Try to connect
        conn = db_manager.get_user_connection(user_id)
        print("✓ Connection successful")
        
        # Try to query
        cursor = conn.cursor()
        
        # Check for tables
        if hasattr(cursor, 'execute'):
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"✓ Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        
        print("✓ Test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def enable_multi_tenant_mode():
    """Enable multi-tenant mode for the application"""
    print("\nEnabling multi-tenant mode...")
    
    try:
        db = DatabaseConnection.get_instance()
        db.enable_multi_tenant(True)
        
        print("✓ Multi-tenant mode enabled")
        print("\nTo make this persistent, set environment variable:")
        print("  SET MULTI_TENANT_MODE=true")
        print("\nOr add to your .env file:")
        print("  MULTI_TENANT_MODE=true")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Main setup function"""
    print("="*60)
    print("User Database Setup Utility")
    print("="*60)
    
    print("\nThis utility helps you set up individual databases for users.")
    print("\nOptions:")
    print("1. Create User_Database_Config table")
    print("2. Initialize database for a specific user")
    print("3. Initialize databases for all users")
    print("4. Test user database connection")
    print("5. Enable multi-tenant mode")
    print("6. Exit")
    
    while True:
        print("\n" + "-"*60)
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            setup_user_database_table()
            
        elif choice == '2':
            user_id = input("Enter User ID: ").strip()
            if user_id.isdigit():
                db_type = input("Database type (sqlite/sqlserver) [sqlite]: ").strip() or 'sqlite'
                
                if db_type == 'sqlserver':
                    db_host = input("Database Host: ").strip()
                    db_port = input("Database Port [1433]: ").strip() or '1433'
                    db_name = input("Database Name: ").strip()
                    db_user = input("Database User: ").strip()
                    db_password = input("Database Password: ").strip()
                    
                    initialize_user_database(
                        int(user_id),
                        db_type='sqlserver',
                        db_host=db_host,
                        db_port=int(db_port),
                        db_name=db_name,
                        db_user=db_user,
                        db_password=db_password
                    )
                else:
                    initialize_user_database(int(user_id), db_type='sqlite')
            else:
                print("Invalid User ID")
                
        elif choice == '3':
            confirm = input("Initialize databases for ALL users? (yes/no): ").strip().lower()
            if confirm == 'yes':
                initialize_all_users()
            else:
                print("Cancelled")
                
        elif choice == '4':
            user_id = input("Enter User ID to test: ").strip()
            if user_id.isdigit():
                test_user_database(int(user_id))
            else:
                print("Invalid User ID")
                
        elif choice == '5':
            enable_multi_tenant_mode()
            
        elif choice == '6':
            print("\nExiting...")
            break
            
        else:
            print("Invalid option")


if __name__ == '__main__':
    main()
