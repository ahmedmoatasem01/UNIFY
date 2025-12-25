from core.db_singleton import DatabaseConnection
from models.deadline_notification import DeadlineNotification
from datetime import datetime


class DeadlineNotificationRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all deadline notifications"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Notification_ID, User_ID, Deadline_Type, Source_ID, Source_Type, 
                       Deadline_Date, Title, Description, Priority, Status, Created_At
                FROM [DeadlineNotification]
            """)
            rows = cursor.fetchall()
            notifications = []
            for row in rows:
                notifications.append(self._row_to_notification(row))
            return notifications
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, notification_id):
        """Get deadline notification by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Notification_ID, User_ID, Deadline_Type, Source_ID, Source_Type, 
                       Deadline_Date, Title, Description, Priority, Status, Created_At
                FROM [DeadlineNotification]
                WHERE Notification_ID = ?
            """, (notification_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_notification(row)
            return None
        finally:
            cursor.close()
            conn.close()

    def get_by_user_id(self, user_id):
        """Get all deadline notifications for a user"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Notification_ID, User_ID, Deadline_Type, Source_ID, Source_Type, 
                       Deadline_Date, Title, Description, Priority, Status, Created_At
                FROM [DeadlineNotification]
                WHERE User_ID = ?
                ORDER BY Deadline_Date ASC
            """, (user_id,))
            rows = cursor.fetchall()
            notifications = []
            for row in rows:
                notifications.append(self._row_to_notification(row))
            return notifications
        finally:
            cursor.close()
            conn.close()

    def get_upcoming(self, user_id, limit=10):
        """Get upcoming deadline notifications for a user"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP (?) Notification_ID, User_ID, Deadline_Type, Source_ID, Source_Type, 
                       Deadline_Date, Title, Description, Priority, Status, Created_At
                FROM [DeadlineNotification]
                WHERE User_ID = ? AND Status = 'active' AND Deadline_Date >= GETDATE()
                ORDER BY Deadline_Date ASC
            """, (limit, user_id))
            rows = cursor.fetchall()
            notifications = []
            for row in rows:
                notifications.append(self._row_to_notification(row))
            return notifications
        finally:
            cursor.close()
            conn.close()

    def get_urgent(self, user_id, hours=24):
        """Get urgent deadline notifications (within specified hours)"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Notification_ID, User_ID, Deadline_Type, Source_ID, Source_Type, 
                       Deadline_Date, Title, Description, Priority, Status, Created_At
                FROM [DeadlineNotification]
                WHERE User_ID = ? AND Status = 'active'
                  AND Deadline_Date >= GETDATE()
                  AND Deadline_Date <= DATEADD(HOUR, ?, GETDATE())
                ORDER BY Deadline_Date ASC
            """, (user_id, hours))
            rows = cursor.fetchall()
            notifications = []
            for row in rows:
                notifications.append(self._row_to_notification(row))
            return notifications
        finally:
            cursor.close()
            conn.close()

    def get_by_source(self, source_type, source_id):
        """Get deadline notifications by source"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Notification_ID, User_ID, Deadline_Type, Source_ID, Source_Type, 
                       Deadline_Date, Title, Description, Priority, Status, Created_At
                FROM [DeadlineNotification]
                WHERE Source_Type = ? AND Source_ID = ?
            """, (source_type, source_id))
            rows = cursor.fetchall()
            notifications = []
            for row in rows:
                notifications.append(self._row_to_notification(row))
            return notifications
        finally:
            cursor.close()
            conn.close()

    def create(self, notification):
        """Create a new deadline notification"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO [DeadlineNotification] 
                (User_ID, Deadline_Type, Source_ID, Source_Type, Deadline_Date, Title, Description, Priority, Status, Created_At)
                OUTPUT INSERTED.Notification_ID
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                notification.User_ID,
                notification.Deadline_Type,
                notification.Source_ID,
                notification.Source_Type,
                notification.Deadline_Date,
                notification.Title,
                notification.Description,
                notification.Priority,
                notification.Status,
                notification.Created_At
            ))
            row = cursor.fetchone()
            notification_id = row[0] if row else None
            conn.commit()
            if notification_id:
                notification.Notification_ID = notification_id
            return notification
        finally:
            cursor.close()
            conn.close()

    def update(self, notification):
        """Update a deadline notification"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE [DeadlineNotification]
                SET Deadline_Type = ?, Source_ID = ?, Source_Type = ?, Deadline_Date = ?,
                    Title = ?, Description = ?, Priority = ?, Status = ?
                WHERE Notification_ID = ?
            """, (
                notification.Deadline_Type,
                notification.Source_ID,
                notification.Source_Type,
                notification.Deadline_Date,
                notification.Title,
                notification.Description,
                notification.Priority,
                notification.Status,
                notification.Notification_ID
            ))
            conn.commit()
            return notification
        finally:
            cursor.close()
            conn.close()

    def delete(self, notification_id):
        """Delete a deadline notification"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [DeadlineNotification] WHERE Notification_ID = ?", (notification_id,))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    def mark_completed(self, notification_id):
        """Mark a deadline notification as completed"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE [DeadlineNotification]
                SET Status = 'completed'
                WHERE Notification_ID = ?
            """, (notification_id,))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    def mark_overdue(self, notification_id):
        """Mark a deadline notification as overdue"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE [DeadlineNotification]
                SET Status = 'overdue'
                WHERE Notification_ID = ?
            """, (notification_id,))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    def _row_to_notification(self, row):
        """Convert database row to DeadlineNotification object"""
        deadline_date = row[5]
        if deadline_date and isinstance(deadline_date, str):
            try:
                deadline_date = datetime.fromisoformat(deadline_date.replace('Z', '+00:00'))
            except:
                try:
                    deadline_date = datetime.strptime(deadline_date, '%Y-%m-%d %H:%M:%S')
                except:
                    deadline_date = None
        
        created_at = row[10] if len(row) > 10 else None
        if created_at and isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                try:
                    created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                except:
                    created_at = None
        
        return DeadlineNotification(
            Notification_ID=row[0],
            User_ID=row[1],
            Deadline_Type=row[2],
            Source_ID=row[3],
            Source_Type=row[4],
            Deadline_Date=deadline_date,
            Title=row[6],
            Description=row[7],
            Priority=row[8],
            Status=row[9],
            Created_At=created_at
        )

