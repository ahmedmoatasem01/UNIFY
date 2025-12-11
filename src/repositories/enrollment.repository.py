from core.db_singleton import DatabaseConnection
from models.enrollment import Enrollment


class EnrollmentRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all enrollments"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Enrollment_ID, Student_ID, Course_ID, Status, Grade, Semester FROM [Enrollment]")
            rows = cursor.fetchall()
            enrollments = []
            for row in rows:
                enrollments.append(Enrollment(
                    Enrollment_ID=row[0],
                    Student_ID=row[1],
                    Course_ID=row[2],
                    Status=row[3],
                    Grade=row[4],
                    Semester=row[5]
                ))
            return enrollments
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, enrollment_id):
        """Get enrollment by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Enrollment_ID, Student_ID, Course_ID, Status, Grade, Semester FROM [Enrollment] WHERE Enrollment_ID = ?", (enrollment_id,))
            row = cursor.fetchone()
            if row:
                return Enrollment(
                    Enrollment_ID=row[0],
                    Student_ID=row[1],
                    Course_ID=row[2],
                    Status=row[3],
                    Grade=row[4],
                    Semester=row[5]
                )
            return None
        finally:
            cursor.close()
            conn.close()

    def get_by_student(self, student_id):
        """Get all enrollments for a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Enrollment_ID, Student_ID, Course_ID, Status, Grade, Semester FROM [Enrollment] WHERE Student_ID = ?", (student_id,))
            rows = cursor.fetchall()
            enrollments = []
            for row in rows:
                enrollments.append(Enrollment(
                    Enrollment_ID=row[0],
                    Student_ID=row[1],
                    Course_ID=row[2],
                    Status=row[3],
                    Grade=row[4],
                    Semester=row[5]
                ))
            return enrollments
        finally:
            cursor.close()
            conn.close()
    
    def get_by_student_id(self, student_id):
        """Get all enrollments for a student (alias for get_by_student)"""
        return self.get_by_student(student_id)

    def get_by_course(self, course_id):
        """Get all enrollments for a course"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Enrollment_ID, Student_ID, Course_ID, Status, Grade, Semester FROM [Enrollment] WHERE Course_ID = ?", (course_id,))
            rows = cursor.fetchall()
            enrollments = []
            for row in rows:
                enrollments.append(Enrollment(
                    Enrollment_ID=row[0],
                    Student_ID=row[1],
                    Course_ID=row[2],
                    Status=row[3],
                    Grade=row[4],
                    Semester=row[5]
                ))
            return enrollments
        finally:
            cursor.close()
            conn.close()

    def create(self, enrollment):
        """Create a new enrollment"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO [Enrollment] (Student_ID, Course_ID, Status, Grade, Semester) VALUES (?, ?, ?, ?, ?)",
                (enrollment.Student_ID, enrollment.Course_ID, enrollment.Status, enrollment.Grade, enrollment.Semester)
            )
            conn.commit()
            # Get the last inserted ID for SQL Server
            cursor.execute("SELECT SCOPE_IDENTITY()")
            enrollment.Enrollment_ID = cursor.fetchone()[0]
            return enrollment
        finally:
            cursor.close()
            conn.close()

    def update(self, enrollment):
        """Update an existing enrollment"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE [Enrollment] SET Status = ?, Grade = ?, Semester = ? WHERE Enrollment_ID = ?",
                (enrollment.Status, enrollment.Grade, enrollment.Semester, enrollment.Enrollment_ID)
            )
            conn.commit()
            return enrollment
        finally:
            cursor.close()
            conn.close()

    def delete(self, enrollment_id):
        """Delete an enrollment by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [Enrollment] WHERE Enrollment_ID = ?", (enrollment_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

