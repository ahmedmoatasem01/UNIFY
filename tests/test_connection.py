"""
Test database connection script
Run this to verify your database connection is working
"""
import sys
import os

# Add parent directory to path to import core module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_singleton import DatabaseConnection

def test_connection():
    """Test the database connection"""
    try:
        db = DatabaseConnection()
        conn = db.get_connection()
        
        if conn and conn.is_connected():
            print("[OK] Successfully connected to MySQL database 'unify'")
            
            # Test query - show all tables
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print(f"\n[OK] Found {len(tables)} table(s) in the database:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Test a simple query on User table
            try:
                cursor.execute("SELECT COUNT(*) FROM `User`")
                count = cursor.fetchone()[0]
                print(f"\n[OK] User table is accessible (contains {count} record(s))")
            except Exception as e:
                print(f"\n[WARNING] User table query failed: {e}")
                print("  (This is okay if the table is empty or doesn't exist yet)")
            
            cursor.close()
            return True
        else:
            print("[ERROR] Failed to connect to database")
            return False
            
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
        print("\nPlease check:")
        print("  1. MySQL server is running")
        print("  2. Database 'unify' exists")
        print("  3. Username and password in db_singleton.py are correct")
        print("\nTo start MySQL on Windows:")
        print("  - Open Services (services.msc)")
        print("  - Find 'MySQL' service and start it")
        print("  - Or use: net start MySQL")
        return False

if __name__ == "__main__":
    test_connection()

