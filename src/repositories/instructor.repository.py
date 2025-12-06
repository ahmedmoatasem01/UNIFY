from core.db_singleton import DatabaseConnection
from models.instructor import Instructor


class InstructorRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all instructors"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Instructor_ID, User_ID, Department, Office, Email FROM Instructor")
            rows = cursor.fetchall()
            instructors = []
            for row in rows:
                instructors.append(Instructor(
                    Instructor_ID=row[0],
                    User_ID=row[1],
                    Department=row[2],
                    Office=row[3],
                    Email=row[4]
                ))
            return instructors
        finally:
            conn.close()

    def get_by_id(self, instructor_id):
        """Get instructor by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Instructor_ID, User_ID, Department, Office, Email FROM Instructor WHERE Instructor_ID = ?", (instructor_id,))
            row = cursor.fetchone()
            if row:
                return Instructor(
                    Instructor_ID=row[0],
                    User_ID=row[1],
                    Department=row[2],
                    Office=row[3],
                    Email=row[4]
                )
            return None
        finally:
            conn.close()

    def get_by_user_id(self, user_id):
        """Get instructor by User_ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Instructor_ID, User_ID, Department, Office, Email FROM Instructor WHERE User_ID = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return Instructor(
                    Instructor_ID=row[0],
                    User_ID=row[1],
                    Department=row[2],
                    Office=row[3],
                    Email=row[4]
                )
            return None
        finally:
            conn.close()

    def create(self, instructor):
        """Create a new instructor"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Instructor (User_ID, Department, Office, Email) OUTPUT INSERTED.Instructor_ID VALUES (?, ?, ?, ?)",
                (instructor.User_ID, instructor.Department, instructor.Office, instructor.Email)
            )
            instructor_id = cursor.fetchone()[0]
            conn.commit()
            instructor.Instructor_ID = instructor_id
            return instructor
        finally:
            conn.close()

    def update(self, instructor):
        """Update an existing instructor"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Instructor SET Department = ?, Office = ?, Email = ? WHERE Instructor_ID = ?",
                (instructor.Department, instructor.Office, instructor.Email, instructor.Instructor_ID)
            )
            conn.commit()
            return instructor
        finally:
            conn.close()

    def delete(self, instructor_id):
        """Delete an instructor by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Instructor WHERE Instructor_ID = ?", (instructor_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

