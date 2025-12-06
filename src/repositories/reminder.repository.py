from core.db_singleton import DatabaseConnection
from models.reminder import Reminder


class ReminderRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all reminders"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Reminder_ID, Student_ID, Event_ID, Reminder_Time, Status FROM Reminder")
            rows = cursor.fetchall()
            reminders = []
            for row in rows:
                reminders.append(Reminder(
                    Reminder_ID=row[0],
                    Student_ID=row[1],
                    Event_ID=row[2],
                    Reminder_Time=row[3],
                    Status=row[4]
                ))
            return reminders
        finally:
            conn.close()

    def get_by_id(self, reminder_id):
        """Get reminder by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Reminder_ID, Student_ID, Event_ID, Reminder_Time, Status FROM Reminder WHERE Reminder_ID = ?", (reminder_id,))
            row = cursor.fetchone()
            if row:
                return Reminder(
                    Reminder_ID=row[0],
                    Student_ID=row[1],
                    Event_ID=row[2],
                    Reminder_Time=row[3],
                    Status=row[4]
                )
            return None
        finally:
            conn.close()

    def get_by_student(self, student_id):
        """Get all reminders for a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Reminder_ID, Student_ID, Event_ID, Reminder_Time, Status FROM Reminder WHERE Student_ID = ? ORDER BY Reminder_Time", (student_id,))
            rows = cursor.fetchall()
            reminders = []
            for row in rows:
                reminders.append(Reminder(
                    Reminder_ID=row[0],
                    Student_ID=row[1],
                    Event_ID=row[2],
                    Reminder_Time=row[3],
                    Status=row[4]
                ))
            return reminders
        finally:
            conn.close()

    def get_pending(self, student_id=None):
        """Get all pending reminders"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            if student_id:
                cursor.execute("SELECT Reminder_ID, Student_ID, Event_ID, Reminder_Time, Status FROM Reminder WHERE Status = 'pending' AND Student_ID = ? ORDER BY Reminder_Time", (student_id,))
            else:
                cursor.execute("SELECT Reminder_ID, Student_ID, Event_ID, Reminder_Time, Status FROM Reminder WHERE Status = 'pending' ORDER BY Reminder_Time")
            rows = cursor.fetchall()
            reminders = []
            for row in rows:
                reminders.append(Reminder(
                    Reminder_ID=row[0],
                    Student_ID=row[1],
                    Event_ID=row[2],
                    Reminder_Time=row[3],
                    Status=row[4]
                ))
            return reminders
        finally:
            conn.close()

    def create(self, reminder):
        """Create a new reminder"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Reminder (Student_ID, Event_ID, Reminder_Time, Status) OUTPUT INSERTED.Reminder_ID VALUES (?, ?, ?, ?)",
                (reminder.Student_ID, reminder.Event_ID, reminder.Reminder_Time, reminder.Status)
            )
            reminder_id = cursor.fetchone()[0]
            conn.commit()
            reminder.Reminder_ID = reminder_id
            return reminder
        finally:
            conn.close()

    def update(self, reminder):
        """Update an existing reminder"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Reminder SET Reminder_Time = ?, Status = ? WHERE Reminder_ID = ?",
                (reminder.Reminder_Time, reminder.Status, reminder.Reminder_ID)
            )
            conn.commit()
            return reminder
        finally:
            conn.close()

    def delete(self, reminder_id):
        """Delete a reminder by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Reminder WHERE Reminder_ID = ?", (reminder_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

