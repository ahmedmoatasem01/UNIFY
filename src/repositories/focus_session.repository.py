from core.db_singleton import DatabaseConnection
from models.focus_session import FocusSession


class FocusSessionRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all focus sessions"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Session_ID, Student_ID, Duration, Start_Time, End_Time, Completed FROM Focus_Session")
            rows = cursor.fetchall()
            sessions = []
            for row in rows:
                sessions.append(FocusSession(
                    Session_ID=row[0],
                    Student_ID=row[1],
                    Duration=row[2],
                    Start_Time=row[3],
                    End_Time=row[4],
                    Completed=bool(row[5])
                ))
            return sessions
        finally:
            conn.close()

    def get_by_id(self, session_id):
        """Get focus session by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Session_ID, Student_ID, Duration, Start_Time, End_Time, Completed FROM Focus_Session WHERE Session_ID = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                return FocusSession(
                    Session_ID=row[0],
                    Student_ID=row[1],
                    Duration=row[2],
                    Start_Time=row[3],
                    End_Time=row[4],
                    Completed=bool(row[5])
                )
            return None
        finally:
            conn.close()

    def get_by_student(self, student_id):
        """Get all focus sessions for a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Session_ID, Student_ID, Duration, Start_Time, End_Time, Completed FROM Focus_Session WHERE Student_ID = ? ORDER BY Start_Time DESC", (student_id,))
            rows = cursor.fetchall()
            sessions = []
            for row in rows:
                sessions.append(FocusSession(
                    Session_ID=row[0],
                    Student_ID=row[1],
                    Duration=row[2],
                    Start_Time=row[3],
                    End_Time=row[4],
                    Completed=bool(row[5])
                ))
            return sessions
        finally:
            conn.close()

    def create(self, session):
        """Create a new focus session"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Focus_Session (Student_ID, Duration, Start_Time, End_Time, Completed) OUTPUT INSERTED.Session_ID VALUES (?, ?, ?, ?, ?)",
                (session.Student_ID, session.Duration, session.Start_Time, session.End_Time, 1 if session.Completed else 0)
            )
            session_id = cursor.fetchone()[0]
            conn.commit()
            session.Session_ID = session_id
            return session
        finally:
            conn.close()

    def update(self, session):
        """Update an existing focus session"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Focus_Session SET Duration = ?, Start_Time = ?, End_Time = ?, Completed = ? WHERE Session_ID = ?",
                (session.Duration, session.Start_Time, session.End_Time, 1 if session.Completed else 0, session.Session_ID)
            )
            conn.commit()
            return session
        finally:
            conn.close()

    def delete(self, session_id):
        """Delete a focus session by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Focus_Session WHERE Session_ID = ?", (session_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

