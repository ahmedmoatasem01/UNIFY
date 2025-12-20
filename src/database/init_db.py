"""
Database initialization script
Run this script to create all database tables
"""
import mysql.connector
from mysql.connector import Error
import os

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Change if you set a password
    'database': 'unify'  # Change from 'shopease' to 'unify'
}

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect without specifying database
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"Database '{DB_CONFIG['database']}' created or already exists")
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error creating database: {e}")

def init_tables():
    """Initialize all database tables from schema.sql"""
    try:
        # Create database first
        create_database()
        
        # Connect to the database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Read and execute schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Split by semicolon and execute each statement
        # Filter out comments and empty statements
        statements = []
        for s in schema_sql.split(';'):
            s = s.strip()
            # Skip empty statements and comment-only lines
            if s and not s.startswith('--'):
                # Remove inline comments
                lines = [line for line in s.split('\n') 
                        if line.strip() and not line.strip().startswith('--')]
                if lines:
                    statements.append('\n'.join(lines))
        
        for statement in statements:
            try:
                # Skip USE statements (we're already connected to the database)
                if statement.upper().strip().startswith('USE'):
                    continue
                cursor.execute(statement)
                # Extract table name for better logging
                if 'CREATE TABLE' in statement.upper():
                    table_name = statement.split('`')[1] if '`' in statement else 'table'
                    print(f"✓ Created table: {table_name}")
            except Error as e:
                print(f"Warning: {e}")
                print(f"  Statement: {statement[:100]}...")
        
        conn.commit()
        print("\n✓ Database tables created successfully!")
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"Error initializing tables: {e}")

if __name__ == "__main__":
    init_tables()

