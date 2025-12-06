import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="", # your MySQL root password
    database="shopease"
)

print(conn.is_connected()) # Should print True