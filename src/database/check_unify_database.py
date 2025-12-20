"""
Check if unify database exists and can be connected
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_singleton import DatabaseConnection

def check_database():
    """Check if we can connect to the unify database"""
    print("Checking connection to UNIFY database...")
    print("-" * 50)
    
    try:
        db = DatabaseConnection()
        conn = db.get_connection()
        
        if conn:
            print("[OK] Successfully connected to SQL Server")
            
            # Check if unify database exists
            cursor = conn.cursor()
            
            # Check current database
            cursor.execute("SELECT DB_NAME() AS CurrentDatabase")
            current_db = cursor.fetchone()[0]
            print(f"\nCurrent database: {current_db}")
            
            # List all databases
            cursor.execute("""
                SELECT name 
                FROM sys.databases 
                WHERE name = 'unify'
            """)
            result = cursor.fetchone()
            
            if result:
                print("[OK] Database 'unify' exists!")
                
                # Switch to unify database
                cursor.execute("USE unify")
                
                # Check existing tables
                cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_TYPE = 'BASE TABLE'
                    ORDER BY TABLE_NAME
                """)
                tables = cursor.fetchall()
                
                print(f"\n[OK] Found {len(tables)} table(s) in 'unify' database:")
                for table in tables:
                    print(f"  - {table[0]}")
                
                # Check if CourseMaterial table exists
                cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'CourseMaterial'
                """)
                if cursor.fetchone():
                    print("\n[OK] CourseMaterial table exists!")
                else:
                    print("\n[INFO] CourseMaterial table does NOT exist yet.")
                    print("       Run: src/database/migrations/create_course_materials_table.sql")
                
            else:
                print("\n[WARNING] Database 'unify' does NOT exist!")
                print("\nTo create it:")
                print("1. Open SQL Server Management Studio")
                print("2. Connect to: DESKTOP-V6DPJFP\\SQLEXPRESS")
                print("3. Right-click 'Databases' → New Database")
                print("4. Name: unify")
                print("5. Click OK")
            
            cursor.close()
            conn.close()
            return True
            
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure SQL Server is running")
        print("2. Check server name: DESKTOP-V6DPJFP\\SQLEXPRESS")
        print("3. Try connecting manually in SSMS first")
        return False

if __name__ == "__main__":
    success = check_database()
    sys.exit(0 if success else 1)

