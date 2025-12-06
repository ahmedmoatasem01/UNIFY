from core.db_singleton import DatabaseConnection
from models.course import Course


class CourseRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all courses"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Course_ID, Course_Name, Credits, Instructor_ID, Schedule FROM Course")
            rows = cursor.fetchall()
            courses = []
            for row in rows:
                courses.append(Course(
                    Course_ID=row[0],
                    Course_Name=row[1],
                    Credits=row[2],
                    Instructor_ID=row[3],
                    Schedule=row[4]
                ))
            return courses
        finally:
            conn.close()

    def get_by_id(self, course_id):
        """Get course by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Course_ID, Course_Name, Credits, Instructor_ID, Schedule FROM Course WHERE Course_ID = ?", (course_id,))
            row = cursor.fetchone()
            if row:
                return Course(
                    Course_ID=row[0],
                    Course_Name=row[1],
                    Credits=row[2],
                    Instructor_ID=row[3],
                    Schedule=row[4]
                )
            return None
        finally:
            conn.close()

    def get_by_instructor(self, instructor_id):
        """Get all courses by instructor"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Course_ID, Course_Name, Credits, Instructor_ID, Schedule FROM Course WHERE Instructor_ID = ?", (instructor_id,))
            rows = cursor.fetchall()
            courses = []
            for row in rows:
                courses.append(Course(
                    Course_ID=row[0],
                    Course_Name=row[1],
                    Credits=row[2],
                    Instructor_ID=row[3],
                    Schedule=row[4]
                ))
            return courses
        finally:
            conn.close()

    def create(self, course):
        """Create a new course"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Course (Course_Name, Credits, Instructor_ID, Schedule) OUTPUT INSERTED.Course_ID VALUES (?, ?, ?, ?)",
                (course.Course_Name, course.Credits, course.Instructor_ID, course.Schedule)
            )
            course_id = cursor.fetchone()[0]
            conn.commit()
            course.Course_ID = course_id
            return course
        finally:
            conn.close()

    def update(self, course):
        """Update an existing course"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Course SET Course_Name = ?, Credits = ?, Instructor_ID = ?, Schedule = ? WHERE Course_ID = ?",
                (course.Course_Name, course.Credits, course.Instructor_ID, course.Schedule, course.Course_ID)
            )
            conn.commit()
            return course
        finally:
            conn.close()

    def delete(self, course_id):
        """Delete a course by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Course WHERE Course_ID = ?", (course_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

