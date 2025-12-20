"""
Test User Settings Database Connection
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.db_singleton import DatabaseConnection

def test_user_settings_table():
    """Test if User_Settings table exists and can be accessed"""
    try:
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'User_Settings'
        """)
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            print("[ERROR] User_Settings table does NOT exist in the database!")
            print("\nTo fix this, run the SQL script:")
            print("  src/database/migrations/create_user_settings_table.sql")
            print("\nOr run the complete setup:")
            print("  src/database/unify_complete_setup.sql")
            cursor.close()
            conn.close()
            return False
        
        print("[OK] User_Settings table exists")
        
        # Check table structure
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'User_Settings'
            ORDER BY ORDINAL_POSITION
        """)
        columns = cursor.fetchall()
        print(f"\n[OK] Table has {len(columns)} columns:")
        for col_name, col_type in columns:
            print(f"  - {col_name} ({col_type})")
        
        # Test a simple query
        cursor.execute("SELECT COUNT(*) FROM User_Settings")
        count = cursor.fetchone()[0]
        print(f"\n[OK] Table is accessible (contains {count} record(s))")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        print("\nMake sure:")
        print("  1. SQL Server is running")
        print("  2. Database 'unify' exists")
        print("  3. User_Settings table exists")
        return False

if __name__ == "__main__":
    print("Testing User_Settings table...")
    print("=" * 50)
    test_user_settings_table()

