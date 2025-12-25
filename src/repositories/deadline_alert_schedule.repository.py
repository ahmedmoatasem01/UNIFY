from core.db_singleton import DatabaseConnection
from models.deadline_alert_schedule import DeadlineAlertSchedule
from datetime import datetime


class DeadlineAlertScheduleRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all alert schedules"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Schedule_ID, Notification_ID, Alert_Time_Before_Deadline, 
                       Alert_Type, Is_Sent, Sent_At
                FROM [DeadlineAlertSchedule]
            """)
            rows = cursor.fetchall()
            schedules = []
            for row in rows:
                schedules.append(self._row_to_schedule(row))
            return schedules
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, schedule_id):
        """Get alert schedule by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Schedule_ID, Notification_ID, Alert_Time_Before_Deadline, 
                       Alert_Type, Is_Sent, Sent_At
                FROM [DeadlineAlertSchedule]
                WHERE Schedule_ID = ?
            """, (schedule_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_schedule(row)
            return None
        finally:
            cursor.close()
            conn.close()

    def get_by_notification_id(self, notification_id):
        """Get all alert schedules for a notification"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Schedule_ID, Notification_ID, Alert_Time_Before_Deadline, 
                       Alert_Type, Is_Sent, Sent_At
                FROM [DeadlineAlertSchedule]
                WHERE Notification_ID = ?
                ORDER BY Alert_Time_Before_Deadline DESC
            """, (notification_id,))
            rows = cursor.fetchall()
            schedules = []
            for row in rows:
                schedules.append(self._row_to_schedule(row))
            return schedules
        finally:
            cursor.close()
            conn.close()

    def get_pending_alerts(self):
        """Get all pending (unsent) alerts"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Schedule_ID, Notification_ID, Alert_Time_Before_Deadline, 
                       Alert_Type, Is_Sent, Sent_At
                FROM [DeadlineAlertSchedule]
                WHERE Is_Sent = 0
            """)
            rows = cursor.fetchall()
            schedules = []
            for row in rows:
                schedules.append(self._row_to_schedule(row))
            return schedules
        finally:
            cursor.close()
            conn.close()

    def create(self, schedule):
        """Create a new alert schedule"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            is_sent_bit = 1 if schedule.Is_Sent else 0
            cursor.execute("""
                INSERT INTO [DeadlineAlertSchedule] 
                (Notification_ID, Alert_Time_Before_Deadline, Alert_Type, Is_Sent, Sent_At)
                OUTPUT INSERTED.Schedule_ID
                VALUES (?, ?, ?, ?, ?)
            """, (
                schedule.Notification_ID,
                schedule.Alert_Time_Before_Deadline,
                schedule.Alert_Type,
                is_sent_bit,
                schedule.Sent_At
            ))
            row = cursor.fetchone()
            schedule_id = row[0] if row else None
            conn.commit()
            if schedule_id:
                schedule.Schedule_ID = schedule_id
            return schedule
        finally:
            cursor.close()
            conn.close()

    def update(self, schedule):
        """Update an alert schedule"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            is_sent_bit = 1 if schedule.Is_Sent else 0
            cursor.execute("""
                UPDATE [DeadlineAlertSchedule]
                SET Notification_ID = ?, Alert_Time_Before_Deadline = ?, 
                    Alert_Type = ?, Is_Sent = ?, Sent_At = ?
                WHERE Schedule_ID = ?
            """, (
                schedule.Notification_ID,
                schedule.Alert_Time_Before_Deadline,
                schedule.Alert_Type,
                is_sent_bit,
                schedule.Sent_At,
                schedule.Schedule_ID
            ))
            conn.commit()
            return schedule
        finally:
            cursor.close()
            conn.close()

    def mark_as_sent(self, schedule_id):
        """Mark an alert schedule as sent"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE [DeadlineAlertSchedule]
                SET Is_Sent = 1, Sent_At = GETDATE()
                WHERE Schedule_ID = ?
            """, (schedule_id,))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    def delete(self, schedule_id):
        """Delete an alert schedule"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [DeadlineAlertSchedule] WHERE Schedule_ID = ?", (schedule_id,))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    def delete_by_notification_id(self, notification_id):
        """Delete all alert schedules for a notification"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [DeadlineAlertSchedule] WHERE Notification_ID = ?", (notification_id,))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    def _row_to_schedule(self, row):
        """Convert database row to DeadlineAlertSchedule object"""
        sent_at = row[5] if len(row) > 5 else None
        if sent_at and isinstance(sent_at, str):
            try:
                sent_at = datetime.fromisoformat(sent_at.replace('Z', '+00:00'))
            except:
                try:
                    sent_at = datetime.strptime(sent_at, '%Y-%m-%d %H:%M:%S')
                except:
                    sent_at = None
        
        # Handle BIT type from SQL Server (returns as bool or int)
        is_sent = row[4] if len(row) > 4 else False
        if isinstance(is_sent, int):
            is_sent = bool(is_sent)
        
        return DeadlineAlertSchedule(
            Schedule_ID=row[0],
            Notification_ID=row[1],
            Alert_Time_Before_Deadline=row[2],
            Alert_Type=row[3],
            Is_Sent=is_sent,
            Sent_At=sent_at
        )

