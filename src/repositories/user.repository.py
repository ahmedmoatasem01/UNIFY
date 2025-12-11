from core.db_singleton import DatabaseConnection
from models.user import User


class UserRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all users"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT User_ID, Username, Email, Password_Hash, Created_At FROM [User]")
            rows = cursor.fetchall()
            users = []
            for row in rows:
                users.append(User(
                    User_ID=row[0],
                    Username=row[1],
                    Email=row[2],
                    Password_Hash=row[3],
                    Created_At=row[4]
                ))
            return users
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, user_id):
        """Get user by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT User_ID, Username, Email, Password_Hash, Created_At FROM [User] WHERE User_ID = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return User(
                    User_ID=row[0],
                    Username=row[1],
                    Email=row[2],
                    Password_Hash=row[3],
                    Created_At=row[4]
                )
            return None
        finally:
            cursor.close()
            conn.close()

    def get_by_email(self, email):
        """Get user by email"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT User_ID, Username, Email, Password_Hash, Created_At FROM [User] WHERE Email = ?", (email,))
            row = cursor.fetchone()
            if row:
                return User(
                    User_ID=row[0],
                    Username=row[1],
                    Email=row[2],
                    Password_Hash=row[3],
                    Created_At=row[4]
                )
            return None
        finally:
            cursor.close()
            conn.close()

    def create(self, user):
        """Create a new user"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO [User] (Username, Email, Password_Hash) "
                "OUTPUT INSERTED.User_ID "
                "VALUES (?, ?, ?)",
                (user.Username, user.Email, user.Password_Hash)
            )
            row = cursor.fetchone()
            if row:
                user.User_ID = row[0]
            conn.commit()
            return user
        finally:
            cursor.close()
            conn.close()

    def update(self, user):
        """Update an existing user"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE [User] SET Username = ?, Email = ?, Password_Hash = ? WHERE User_ID = ?",
                (user.Username, user.Email, user.Password_Hash, user.User_ID)
            )
            conn.commit()
            return user
        finally:
            cursor.close()
            conn.close()

    def delete(self, user_id):
        """Delete a user by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [User] WHERE User_ID = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
  
