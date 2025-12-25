"""
Notification Repository
Handles database operations for notifications
"""
from core.db_singleton import DatabaseConnection
from models.notification import Notification
from datetime import datetime


class NotificationRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()
    
    def create_table(self):
        """Create the Notification table if it doesn't exist"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Notification]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE [Notification] (
                        Notification_ID INT IDENTITY(1,1) PRIMARY KEY,
                        User_ID INT NOT NULL,
                        Title NVARCHAR(255) NOT NULL,
                        Message NVARCHAR(MAX) NOT NULL,
                        Type NVARCHAR(50),
                        Priority NVARCHAR(20) CHECK (Priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
                        Is_Read BIT DEFAULT 0,
                        Action_URL NVARCHAR(500),
                        Created_At DATETIME DEFAULT GETDATE(),
                        Read_At DATETIME,
                        FOREIGN KEY (User_ID) REFERENCES [User](User_ID)
                    )
                END
            """)
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def get_all(self):
        """Get all notifications"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Notification_ID, User_ID, Title, Message, Type, Priority, Is_Read, Action_URL, Created_At, Read_At
                FROM [Notification]
                ORDER BY Created_At DESC
            """)
            rows = cursor.fetchall()
            notifications = []
            for row in rows:
                notifications.append(Notification(
                    Notification_ID=row[0],
                    User_ID=row[1],
                    Title=row[2],
                    Message=row[3],
                    Type=row[4],
                    Priority=row[5],
                    Is_Read=bool(row[6]) if row[6] is not None else False,
                    Action_URL=row[7],
                    Created_At=row[8],
                    Read_At=row[9]
                ))
            return notifications
        finally:
            cursor.close()
            conn.close()
    
    def get_by_id(self, notification_id):
        """Get notification by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Notification_ID, User_ID, Title, Message, Type, Priority, Is_Read, Action_URL, Created_At, Read_At
                FROM [Notification]
                WHERE Notification_ID = ?
            """, (notification_id,))
            row = cursor.fetchone()
            if row:
                return Notification(
                    Notification_ID=row[0],
                    User_ID=row[1],
                    Title=row[2],
                    Message=row[3],
                    Type=row[4],
                    Priority=row[5],
                    Is_Read=bool(row[6]) if row[6] is not None else False,
                    Action_URL=row[7],
                    Created_At=row[8],
                    Read_At=row[9]
                )
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_by_user(self, user_id, limit=None, unread_only=False):
        """Get notifications for a user"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT Notification_ID, User_ID, Title, Message, Type, Priority, Is_Read, Action_URL, Created_At, Read_At
                FROM [Notification]
                WHERE User_ID = ?
            """
            params = [user_id]
            
            if unread_only:
                query += " AND Is_Read = 0"
            
            query += " ORDER BY Created_At DESC"
            
            if limit:
                query = query.replace("SELECT", f"SELECT TOP {limit}")
            
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            notifications = []
            for row in rows:
                notifications.append(Notification(
                    Notification_ID=row[0],
                    User_ID=row[1],
                    Title=row[2],
                    Message=row[3],
                    Type=row[4],
                    Priority=row[5],
                    Is_Read=bool(row[6]) if row[6] is not None else False,
                    Action_URL=row[7],
                    Created_At=row[8],
                    Read_At=row[9]
                ))
            return notifications
        finally:
            cursor.close()
            conn.close()
    
    def get_unread_count(self, user_id):
        """Get count of unread notifications for a user"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM [Notification] 
                WHERE User_ID = ? AND Is_Read = 0
            """, (user_id,))
            row = cursor.fetchone()
            return row[0] if row else 0
        finally:
            cursor.close()
            conn.close()
    
    def create(self, notification):
        """Create a new notification"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO [Notification] (User_ID, Title, Message, Type, Priority, Is_Read, Action_URL, Created_At) "
                "OUTPUT INSERTED.Notification_ID "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (notification.User_ID, notification.Title, notification.Message, notification.Type,
                 notification.Priority, notification.Is_Read, notification.Action_URL, notification.Created_At)
            )
            row = cursor.fetchone()
            if row:
                notification.Notification_ID = row[0]
            conn.commit()
            return notification
        finally:
            cursor.close()
            conn.close()
    
    def mark_as_read(self, notification_id):
        """Mark a notification as read"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE [Notification] 
                SET Is_Read = 1, Read_At = GETDATE()
                WHERE Notification_ID = ?
            """, (notification_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    
    def mark_all_as_read(self, user_id):
        """Mark all notifications for a user as read"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE [Notification] 
                SET Is_Read = 1, Read_At = GETDATE()
                WHERE User_ID = ? AND Is_Read = 0
            """, (user_id,))
            conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conn.close()
    
    def delete(self, notification_id):
        """Delete a notification by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [Notification] WHERE Notification_ID = ?", (notification_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
