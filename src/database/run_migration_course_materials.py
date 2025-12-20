"""
Run migration to create CourseMaterial table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_singleton import DatabaseConnection

def run_migration():
    """Execute the CourseMaterial table creation script"""
    print("Running CourseMaterial table migration...")
    print("-" * 50)
    
    try:
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Read the SQL file
        migration_file = os.path.join(os.path.dirname(__file__), 'migrations', 'create_course_materials_table.sql')
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Split by GO statements (SQL Server batch separator)
        batches = [batch.strip() for batch in sql_script.split('GO') if batch.strip()]
        
        for i, batch in enumerate(batches):
            # Skip USE and PRINT statements that might cause issues
            if batch.upper().startswith('USE ') or batch.upper().startswith('PRINT'):
                print(f"  [{i+1}/{len(batches)}] Skipping: {batch[:50]}...")
                continue
            
            try:
                cursor.execute(batch)
                print(f"  [{i+1}/{len(batches)}] Executed successfully")
            except Exception as e:
                # If table already exists, that's okay
                if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                    print(f"  [{i+1}/{len(batches)}] Table already exists (OK)")
                else:
                    print(f"  [{i+1}/{len(batches)}] Error: {e}")
                    raise
        
        conn.commit()
        
        # Verify table was created
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'CourseMaterial'
        """)
        result = cursor.fetchone()
        
        if result:
            print("\n[OK] CourseMaterial table created successfully!")
            
            # Show table structure
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'CourseMaterial'
                ORDER BY ORDINAL_POSITION
            """)
            columns = cursor.fetchall()
            print(f"\nTable has {len(columns)} columns:")
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"  - {col[0]}: {col[1]} ({nullable})")
        else:
            print("\n[WARNING] Table may not have been created. Please check manually.")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        migration_file = os.path.join(os.path.dirname(__file__), 'migrations', 'create_course_materials_table.sql')
        print(f"\n[ERROR] Migration failed: {e}")
        print("\nPlease run the SQL script manually in SQL Server Management Studio:")
        print(f"  File: {migration_file}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)

