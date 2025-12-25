"""
Notification Preference Repository
Handles database operations for notification preferences
"""
from core.db_singleton import DatabaseConnection
from models.notification_preference import NotificationPreference


class NotificationPreferenceRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()
    
    def create_table(self):
        """Create the NotificationPreference table if it doesn't exist"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[NotificationPreference]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE [NotificationPreference] (
                        Preference_ID INT IDENTITY(1,1) PRIMARY KEY,
                        User_ID INT NOT NULL,
                        Notification_Type NVARCHAR(50),
                        Email_Enabled BIT DEFAULT 0,
                        In_App_Enabled BIT DEFAULT 1,
                        FOREIGN KEY (User_ID) REFERENCES [User](User_ID),
                        UNIQUE (User_ID, Notification_Type)
                    )
                END
            """)
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def get_by_user(self, user_id):
        """Get all preferences for a user"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Preference_ID, User_ID, Notification_Type, Email_Enabled, In_App_Enabled
                FROM [NotificationPreference]
                WHERE User_ID = ?
            """, (user_id,))
            rows = cursor.fetchall()
            preferences = []
            for row in rows:
                preferences.append(NotificationPreference(
                    Preference_ID=row[0],
                    User_ID=row[1],
                    Notification_Type=row[2],
                    Email_Enabled=bool(row[3]) if row[3] is not None else False,
                    In_App_Enabled=bool(row[4]) if row[4] is not None else True
                ))
            return preferences
        finally:
            cursor.close()
            conn.close()
    
    def get_by_user_and_type(self, user_id, notification_type):
        """Get preference for a user and notification type"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Preference_ID, User_ID, Notification_Type, Email_Enabled, In_App_Enabled
                FROM [NotificationPreference]
                WHERE User_ID = ? AND Notification_Type = ?
            """, (user_id, notification_type))
            row = cursor.fetchone()
            if row:
                return NotificationPreference(
                    Preference_ID=row[0],
                    User_ID=row[1],
                    Notification_Type=row[2],
                    Email_Enabled=bool(row[3]) if row[3] is not None else False,
                    In_App_Enabled=bool(row[4]) if row[4] is not None else True
                )
            return None
        finally:
            cursor.close()
            conn.close()
    
    def create_or_update(self, preference):
        """Create or update a preference"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            # Check if exists
            existing = self.get_by_user_and_type(preference.User_ID, preference.Notification_Type)
            if existing:
                # Update
                cursor.execute("""
                    UPDATE [NotificationPreference]
                    SET Email_Enabled = ?, In_App_Enabled = ?
                    WHERE Preference_ID = ?
                """, (preference.Email_Enabled, preference.In_App_Enabled, existing.Preference_ID))
                preference.Preference_ID = existing.Preference_ID
            else:
                # Create
                cursor.execute(
                    "INSERT INTO [NotificationPreference] (User_ID, Notification_Type, Email_Enabled, In_App_Enabled) "
                    "OUTPUT INSERTED.Preference_ID "
                    "VALUES (?, ?, ?, ?)",
                    (preference.User_ID, preference.Notification_Type, preference.Email_Enabled, preference.In_App_Enabled)
                )
                row = cursor.fetchone()
                if row:
                    preference.Preference_ID = row[0]
            conn.commit()
            return preference
        finally:
            cursor.close()
            conn.close()
