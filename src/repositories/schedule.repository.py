from core.db_singleton import DatabaseConnection
from models.schedule import Schedule


class ScheduleRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all schedules"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Schedule_ID, Student_ID, Course_List, Optimized FROM Schedule")
            rows = cursor.fetchall()
            schedules = []
            for row in rows:
                schedules.append(Schedule(
                    Schedule_ID=row[0],
                    Student_ID=row[1],
                    Course_List=row[2],
                    Optimized=bool(row[3])
                ))
            return schedules
        finally:
            conn.close()

    def get_by_id(self, schedule_id):
        """Get schedule by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Schedule_ID, Student_ID, Course_List, Optimized FROM Schedule WHERE Schedule_ID = ?", (schedule_id,))
            row = cursor.fetchone()
            if row:
                return Schedule(
                    Schedule_ID=row[0],
                    Student_ID=row[1],
                    Course_List=row[2],
                    Optimized=bool(row[3])
                )
            return None
        finally:
            conn.close()

    def get_by_student(self, student_id):
        """Get schedule by Student_ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Schedule_ID, Student_ID, Course_List, Optimized FROM Schedule WHERE Student_ID = ?", (student_id,))
            row = cursor.fetchone()
            if row:
                return Schedule(
                    Schedule_ID=row[0],
                    Student_ID=row[1],
                    Course_List=row[2],
                    Optimized=bool(row[3])
                )
            return None
        finally:
            conn.close()

    def create(self, schedule):
        """Create a new schedule"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Schedule (Student_ID, Course_List, Optimized) OUTPUT INSERTED.Schedule_ID VALUES (?, ?, ?)",
                (schedule.Student_ID, schedule.Course_List, 1 if schedule.Optimized else 0)
            )
            schedule_id = cursor.fetchone()[0]
            conn.commit()
            schedule.Schedule_ID = schedule_id
            return schedule
        finally:
            conn.close()

    def update(self, schedule):
        """Update an existing schedule"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Schedule SET Course_List = ?, Optimized = ? WHERE Schedule_ID = ?",
                (schedule.Course_List, 1 if schedule.Optimized else 0, schedule.Schedule_ID)
            )
            conn.commit()
            return schedule
        finally:
            conn.close()

    def delete(self, schedule_id):
        """Delete a schedule by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Schedule WHERE Schedule_ID = ?", (schedule_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

