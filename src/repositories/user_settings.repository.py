"""
User Settings Repository
Handles database operations for user settings
"""
from models.user_settings import UserSettings
from core.db_singleton import DatabaseConnection
from datetime import datetime


class UserSettingsRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_by_user_id(self, user_id: int):
        """Get settings for a specific user"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    Setting_ID, User_ID,
                    email_notifications, push_notifications, 
                    calendar_reminders, assignment_deadlines,
                    sync_google_calendar, calendar_default_view, timezone,
                    theme, language, colorblind_mode, dyslexia_font,
                    profile_visibility, share_schedule,
                    created_at, updated_at
                FROM [User_Settings]
                WHERE User_ID = ?
            """, (user_id,))
            row = cursor.fetchone()
            
            if row:
                return UserSettings(
                    Setting_ID=row[0],
                    User_ID=row[1],
                    email_notifications=bool(row[2]),
                    push_notifications=bool(row[3]),
                    calendar_reminders=bool(row[4]),
                    assignment_deadlines=bool(row[5]),
                    sync_google_calendar=bool(row[6]),
                    calendar_default_view=row[7],
                    timezone=row[8],
                    theme=row[9],
                    language=row[10],
                    colorblind_mode=bool(row[11]),
                    dyslexia_font=bool(row[12]),
                    profile_visibility=row[13],
                    share_schedule=bool(row[14]),
                    created_at=row[15],
                    updated_at=row[16]
                )
            return None
        finally:
            cursor.close()
            conn.close()

    def create(self, settings: UserSettings):
        """Create default settings for a new user"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO [User_Settings] (
                    User_ID, email_notifications, push_notifications,
                    calendar_reminders, assignment_deadlines,
                    sync_google_calendar, calendar_default_view, timezone,
                    theme, language, colorblind_mode, dyslexia_font,
                    profile_visibility, share_schedule
                )
                OUTPUT INSERTED.Setting_ID
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                settings.User_ID,
                1 if settings.email_notifications else 0,
                1 if settings.push_notifications else 0,
                1 if settings.calendar_reminders else 0,
                1 if settings.assignment_deadlines else 0,
                1 if settings.sync_google_calendar else 0,
                settings.calendar_default_view,
                settings.timezone,
                settings.theme,
                settings.language,
                1 if settings.colorblind_mode else 0,
                1 if settings.dyslexia_font else 0,
                settings.profile_visibility,
                1 if settings.share_schedule else 0
            ))
            row = cursor.fetchone()
            if row:
                settings.Setting_ID = row[0]
            conn.commit()
            return settings
        finally:
            cursor.close()
            conn.close()

    def update(self, settings: UserSettings):
        """Update user settings"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE [User_Settings]
                SET 
                    email_notifications = ?,
                    push_notifications = ?,
                    calendar_reminders = ?,
                    assignment_deadlines = ?,
                    sync_google_calendar = ?,
                    calendar_default_view = ?,
                    timezone = ?,
                    theme = ?,
                    language = ?,
                    colorblind_mode = ?,
                    dyslexia_font = ?,
                    profile_visibility = ?,
                    share_schedule = ?,
                    updated_at = GETDATE()
                WHERE User_ID = ?
            """, (
                1 if settings.email_notifications else 0,
                1 if settings.push_notifications else 0,
                1 if settings.calendar_reminders else 0,
                1 if settings.assignment_deadlines else 0,
                1 if settings.sync_google_calendar else 0,
                settings.calendar_default_view,
                settings.timezone,
                settings.theme,
                settings.language,
                1 if settings.colorblind_mode else 0,
                1 if settings.dyslexia_font else 0,
                settings.profile_visibility,
                1 if settings.share_schedule else 0,
                settings.User_ID
            ))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def get_or_create(self, user_id: int):
        """Get settings for user, or create default if they don't exist"""
        settings = self.get_by_user_id(user_id)
        if not settings:
            # Create default settings
            settings = UserSettings(User_ID=user_id)
            settings = self.create(settings)
        return settings

    def delete(self, user_id: int):
        """Delete user settings"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [User_Settings] WHERE User_ID = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

