from core.db_singleton import DatabaseConnection
from models.task import Task


class TaskRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all tasks"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Task_ID, Student_ID, Task_Title, Due_Date, Priority, Status FROM Task")
            rows = cursor.fetchall()
            tasks = []
            for row in rows:
                tasks.append(Task(
                    Task_ID=row[0],
                    Student_ID=row[1],
                    Task_Title=row[2],
                    Due_Date=row[3],
                    Priority=row[4],
                    Status=row[5]
                ))
            return tasks
        finally:
            conn.close()

    def get_by_id(self, task_id):
        """Get task by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Task_ID, Student_ID, Task_Title, Due_Date, Priority, Status FROM Task WHERE Task_ID = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                return Task(
                    Task_ID=row[0],
                    Student_ID=row[1],
                    Task_Title=row[2],
                    Due_Date=row[3],
                    Priority=row[4],
                    Status=row[5]
                )
            return None
        finally:
            conn.close()

    def get_by_student(self, student_id):
        """Get all tasks for a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Task_ID, Student_ID, Task_Title, Due_Date, Priority, Status FROM Task WHERE Student_ID = ?", (student_id,))
            rows = cursor.fetchall()
            tasks = []
            for row in rows:
                tasks.append(Task(
                    Task_ID=row[0],
                    Student_ID=row[1],
                    Task_Title=row[2],
                    Due_Date=row[3],
                    Priority=row[4],
                    Status=row[5]
                ))
            return tasks
        finally:
            conn.close()

    def create(self, task):
        """Create a new task"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Task (Student_ID, Task_Title, Due_Date, Priority, Status) OUTPUT INSERTED.Task_ID VALUES (?, ?, ?, ?, ?)",
                (task.Student_ID, task.Task_Title, task.Due_Date, task.Priority, task.Status)
            )
            task_id = cursor.fetchone()[0]
            conn.commit()
            task.Task_ID = task_id
            return task
        finally:
            conn.close()

    def update(self, task):
        """Update an existing task"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Task SET Task_Title = ?, Due_Date = ?, Priority = ?, Status = ? WHERE Task_ID = ?",
                (task.Task_Title, task.Due_Date, task.Priority, task.Status, task.Task_ID)
            )
            conn.commit()
            return task
        finally:
            conn.close()

    def delete(self, task_id):
        """Delete a task by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Task WHERE Task_ID = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

