"""Quick script to find student by email"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_singleton import DatabaseConnection

db = DatabaseConnection()
conn = db.get_connection()
cursor = conn.cursor()

# Search for ahmed
cursor.execute("""
    SELECT TOP 10 u.Email, u.Username, s.Student_ID 
    FROM [User] u 
    INNER JOIN Student s ON u.User_ID = s.User_ID 
    WHERE u.Email LIKE '%ahmed%' OR u.Username LIKE '%ahmed%'
""")
rows = cursor.fetchall()

print("Found students:")
for row in rows:
    print(f"  Email: {row[0]}, Username: {row[1]}, Student_ID: {row[2]}")

cursor.close()
conn.close()

