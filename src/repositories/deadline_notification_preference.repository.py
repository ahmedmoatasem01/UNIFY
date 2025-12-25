from core.db_singleton import DatabaseConnection
from models.deadline_notification_preference import DeadlineNotificationPreference


class DeadlineNotificationPreferenceRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all preferences"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Preference_ID, User_ID, Deadline_Type, Alert_Intervals, 
                       Email_Enabled, In_App_Enabled, Quiet_Hours_Start, Quiet_Hours_End
                FROM [DeadlineNotificationPreference]
            """)
            rows = cursor.fetchall()
            preferences = []
            for row in rows:
                preferences.append(self._row_to_preference(row))
            return preferences
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, preference_id):
        """Get preference by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Preference_ID, User_ID, Deadline_Type, Alert_Intervals, 
                       Email_Enabled, In_App_Enabled, Quiet_Hours_Start, Quiet_Hours_End
                FROM [DeadlineNotificationPreference]
                WHERE Preference_ID = ?
            """, (preference_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_preference(row)
            return None
        finally:
            cursor.close()
            conn.close()

    def get_by_user_id(self, user_id):
        """Get all preferences for a user"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Preference_ID, User_ID, Deadline_Type, Alert_Intervals, 
                       Email_Enabled, In_App_Enabled, Quiet_Hours_Start, Quiet_Hours_End
                FROM [DeadlineNotificationPreference]
                WHERE User_ID = ?
            """, (user_id,))
            rows = cursor.fetchall()
            preferences = []
            for row in rows:
                preferences.append(self._row_to_preference(row))
            return preferences
        finally:
            cursor.close()
            conn.close()

    def get_by_user_and_type(self, user_id, deadline_type):
        """Get preference for a user and deadline type"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Preference_ID, User_ID, Deadline_Type, Alert_Intervals, 
                       Email_Enabled, In_App_Enabled, Quiet_Hours_Start, Quiet_Hours_End
                FROM [DeadlineNotificationPreference]
                WHERE User_ID = ? AND Deadline_Type = ?
            """, (user_id, deadline_type))
            row = cursor.fetchone()
            if row:
                return self._row_to_preference(row)
            return None
        finally:
            cursor.close()
            conn.close()

    def create(self, preference):
        """Create a new preference"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            email_enabled_bit = 1 if preference.Email_Enabled else 0
            in_app_enabled_bit = 1 if preference.In_App_Enabled else 0
            cursor.execute("""
                INSERT INTO [DeadlineNotificationPreference] 
                (User_ID, Deadline_Type, Alert_Intervals, Email_Enabled, In_App_Enabled, Quiet_Hours_Start, Quiet_Hours_End)
                OUTPUT INSERTED.Preference_ID
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                preference.User_ID,
                preference.Deadline_Type,
                preference.Alert_Intervals,
                email_enabled_bit,
                in_app_enabled_bit,
                preference.Quiet_Hours_Start,
                preference.Quiet_Hours_End
            ))
            row = cursor.fetchone()
            preference_id = row[0] if row else None
            conn.commit()
            if preference_id:
                preference.Preference_ID = preference_id
            return preference
        finally:
            cursor.close()
            conn.close()

    def update(self, preference):
        """Update a preference"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            email_enabled_bit = 1 if preference.Email_Enabled else 0
            in_app_enabled_bit = 1 if preference.In_App_Enabled else 0
            cursor.execute("""
                UPDATE [DeadlineNotificationPreference]
                SET Deadline_Type = ?, Alert_Intervals = ?, Email_Enabled = ?, 
                    In_App_Enabled = ?, Quiet_Hours_Start = ?, Quiet_Hours_End = ?
                WHERE Preference_ID = ?
            """, (
                preference.Deadline_Type,
                preference.Alert_Intervals,
                email_enabled_bit,
                in_app_enabled_bit,
                preference.Quiet_Hours_Start,
                preference.Quiet_Hours_End,
                preference.Preference_ID
            ))
            conn.commit()
            return preference
        finally:
            cursor.close()
            conn.close()

    def upsert(self, preference):
        """Insert or update a preference (based on User_ID and Deadline_Type)"""
        existing = self.get_by_user_and_type(preference.User_ID, preference.Deadline_Type)
        if existing:
            preference.Preference_ID = existing.Preference_ID
            return self.update(preference)
        else:
            return self.create(preference)

    def delete(self, preference_id):
        """Delete a preference"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [DeadlineNotificationPreference] WHERE Preference_ID = ?", (preference_id,))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    def _row_to_preference(self, row):
        """Convert database row to DeadlineNotificationPreference object"""
        # Handle BIT type from SQL Server
        email_enabled = row[4] if len(row) > 4 else False
        if isinstance(email_enabled, int):
            email_enabled = bool(email_enabled)
        
        in_app_enabled = row[5] if len(row) > 5 else True
        if isinstance(in_app_enabled, int):
            in_app_enabled = bool(in_app_enabled)
        
        return DeadlineNotificationPreference(
            Preference_ID=row[0],
            User_ID=row[1],
            Deadline_Type=row[2],
            Alert_Intervals=row[3],
            Email_Enabled=email_enabled,
            In_App_Enabled=in_app_enabled,
            Quiet_Hours_Start=row[6] if len(row) > 6 else None,
            Quiet_Hours_End=row[7] if len(row) > 7 else None
        )

