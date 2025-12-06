from core.db_singleton import DatabaseConnection
from models.calendar import Calendar


class CalendarRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all calendar events"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Event_ID, Student_ID, Title, Date, Time, Source FROM Calendar")
            rows = cursor.fetchall()
            events = []
            for row in rows:
                events.append(Calendar(
                    Event_ID=row[0],
                    Student_ID=row[1],
                    Title=row[2],
                    Date=row[3],
                    Time=row[4],
                    Source=row[5]
                ))
            return events
        finally:
            conn.close()

    def get_by_id(self, event_id):
        """Get calendar event by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Event_ID, Student_ID, Title, Date, Time, Source FROM Calendar WHERE Event_ID = ?", (event_id,))
            row = cursor.fetchone()
            if row:
                return Calendar(
                    Event_ID=row[0],
                    Student_ID=row[1],
                    Title=row[2],
                    Date=row[3],
                    Time=row[4],
                    Source=row[5]
                )
            return None
        finally:
            conn.close()

    def get_by_student(self, student_id):
        """Get all calendar events for a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Event_ID, Student_ID, Title, Date, Time, Source FROM Calendar WHERE Student_ID = ? ORDER BY Date, Time", (student_id,))
            rows = cursor.fetchall()
            events = []
            for row in rows:
                events.append(Calendar(
                    Event_ID=row[0],
                    Student_ID=row[1],
                    Title=row[2],
                    Date=row[3],
                    Time=row[4],
                    Source=row[5]
                ))
            return events
        finally:
            conn.close()

    def create(self, calendar):
        """Create a new calendar event"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Calendar (Student_ID, Title, Date, Time, Source) OUTPUT INSERTED.Event_ID VALUES (?, ?, ?, ?, ?)",
                (calendar.Student_ID, calendar.Title, calendar.Date, calendar.Time, calendar.Source)
            )
            event_id = cursor.fetchone()[0]
            conn.commit()
            calendar.Event_ID = event_id
            return calendar
        finally:
            conn.close()

    def update(self, calendar):
        """Update an existing calendar event"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Calendar SET Title = ?, Date = ?, Time = ?, Source = ? WHERE Event_ID = ?",
                (calendar.Title, calendar.Date, calendar.Time, calendar.Source, calendar.Event_ID)
            )
            conn.commit()
            return calendar
        finally:
            conn.close()

    def delete(self, event_id):
        """Delete a calendar event by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Calendar WHERE Event_ID = ?", (event_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

