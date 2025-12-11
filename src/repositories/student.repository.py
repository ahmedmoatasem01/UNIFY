from core.db_singleton import DatabaseConnection
from models.student import Student


class StudentRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all students"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Student_ID, User_ID, Department, Year_Level, GPA FROM [Student]")
            rows = cursor.fetchall()
            students = []
            for row in rows:
                students.append(Student(
                    Student_ID=row[0],
                    User_ID=row[1],
                    Department=row[2],
                    Year_Level=row[3],
                    GPA=row[4]
                ))
            return students
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, student_id):
        """Get student by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Student_ID, User_ID, Department, Year_Level, GPA FROM [Student] WHERE Student_ID = ?", (student_id,))
            row = cursor.fetchone()
            if row:
                return Student(
                    Student_ID=row[0],
                    User_ID=row[1],
                    Department=row[2],
                    Year_Level=row[3],
                    GPA=row[4]
                )
            return None
        finally:
            cursor.close()
            conn.close()

    def get_by_user_id(self, user_id):
        """Get student by User_ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Student_ID, User_ID, Department, Year_Level, GPA FROM [Student] WHERE User_ID = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return Student(
                    Student_ID=row[0],
                    User_ID=row[1],
                    Department=row[2],
                    Year_Level=row[3],
                    GPA=row[4]
                )
            return None
        finally:
            cursor.close()
            conn.close()

    def create(self, student):
        """Create a new student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO [Student] (User_ID, Department, Year_Level, GPA) VALUES (?, ?, ?, ?)",
                (student.User_ID, student.Department, student.Year_Level, student.GPA)
            )
            conn.commit()
            # Get the last inserted ID for SQL Server
            cursor.execute("SELECT SCOPE_IDENTITY()")
            student.Student_ID = cursor.fetchone()[0]
            return student
        finally:
            cursor.close()
            conn.close()

    def update(self, student):
        """Update an existing student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE [Student] SET Department = ?, Year_Level = ?, GPA = ? WHERE Student_ID = ?",
                (student.Department, student.Year_Level, student.GPA, student.Student_ID)
            )
            conn.commit()
            return student
        finally:
            cursor.close()
            conn.close()

    def delete(self, student_id):
        """Delete a student by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [Student] WHERE Student_ID = ?", (student_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

