from core.db_singleton import DatabaseConnection
from models.teaching_assistant import TeachingAssistant


class TeachingAssistantRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all teaching assistants"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT TA_ID, User_ID, Assigned_Course_ID, Role, Hours_Per_Week FROM Teaching_Assistant")
            rows = cursor.fetchall()
            tas = []
            for row in rows:
                tas.append(TeachingAssistant(
                    TA_ID=row[0],
                    User_ID=row[1],
                    Assigned_Course_ID=row[2],
                    Role=row[3],
                    Hours_Per_Week=row[4]
                ))
            return tas
        finally:
            conn.close()

    def get_by_id(self, ta_id):
        """Get teaching assistant by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT TA_ID, User_ID, Assigned_Course_ID, Role, Hours_Per_Week FROM Teaching_Assistant WHERE TA_ID = ?", (ta_id,))
            row = cursor.fetchone()
            if row:
                return TeachingAssistant(
                    TA_ID=row[0],
                    User_ID=row[1],
                    Assigned_Course_ID=row[2],
                    Role=row[3],
                    Hours_Per_Week=row[4]
                )
            return None
        finally:
            conn.close()

    def get_by_user_id(self, user_id):
        """Get teaching assistant by User_ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT TA_ID, User_ID, Assigned_Course_ID, Role, Hours_Per_Week FROM Teaching_Assistant WHERE User_ID = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return TeachingAssistant(
                    TA_ID=row[0],
                    User_ID=row[1],
                    Assigned_Course_ID=row[2],
                    Role=row[3],
                    Hours_Per_Week=row[4]
                )
            return None
        finally:
            conn.close()

    def get_by_course(self, course_id):
        """Get all TAs for a course"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT TA_ID, User_ID, Assigned_Course_ID, Role, Hours_Per_Week FROM Teaching_Assistant WHERE Assigned_Course_ID = ?", (course_id,))
            rows = cursor.fetchall()
            tas = []
            for row in rows:
                tas.append(TeachingAssistant(
                    TA_ID=row[0],
                    User_ID=row[1],
                    Assigned_Course_ID=row[2],
                    Role=row[3],
                    Hours_Per_Week=row[4]
                ))
            return tas
        finally:
            conn.close()

    def create(self, ta):
        """Create a new teaching assistant"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Teaching_Assistant (User_ID, Assigned_Course_ID, Role, Hours_Per_Week) OUTPUT INSERTED.TA_ID VALUES (?, ?, ?, ?)",
                (ta.User_ID, ta.Assigned_Course_ID, ta.Role, ta.Hours_Per_Week)
            )
            ta_id = cursor.fetchone()[0]
            conn.commit()
            ta.TA_ID = ta_id
            return ta
        finally:
            conn.close()

    def update(self, ta):
        """Update an existing teaching assistant"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Teaching_Assistant SET Assigned_Course_ID = ?, Role = ?, Hours_Per_Week = ? WHERE TA_ID = ?",
                (ta.Assigned_Course_ID, ta.Role, ta.Hours_Per_Week, ta.TA_ID)
            )
            conn.commit()
            return ta
        finally:
            conn.close()

    def delete(self, ta_id):
        """Delete a teaching assistant by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Teaching_Assistant WHERE TA_ID = ?", (ta_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

