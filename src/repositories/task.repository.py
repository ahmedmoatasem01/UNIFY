from core.db_singleton import DatabaseConnection
from models.task import Task
from datetime import datetime


class TaskRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all tasks"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Task_ID, Student_ID, Task_Title, Due_Date, Priority, Status FROM [Task]")
            rows = cursor.fetchall()
            tasks = []
            for row in rows:
                # Handle Due_Date - convert to datetime if it's a string or keep as datetime
                due_date = row[3]
                if due_date and isinstance(due_date, str):
                    try:
                        due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    except:
                        try:
                            due_date = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
                        except:
                            due_date = None
                
                tasks.append(Task(
                    Task_ID=row[0],
                    Student_ID=row[1],
                    Task_Title=row[2],
                    Due_Date=due_date,
                    Priority=row[4],
                    Status=row[5]
                ))
            return tasks
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, task_id):
        """Get task by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Task_ID, Student_ID, Task_Title, Due_Date, Priority, Status FROM [Task] WHERE Task_ID = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                # Handle Due_Date - convert to datetime if needed
                due_date = row[3]
                if due_date and isinstance(due_date, str):
                    try:
                        due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    except:
                        try:
                            due_date = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
                        except:
                            due_date = None
                
                return Task(
                    Task_ID=row[0],
                    Student_ID=row[1],
                    Task_Title=row[2],
                    Due_Date=due_date,
                    Priority=row[4],
                    Status=row[5]
                )
            return None
        finally:
            cursor.close()
            conn.close()

    def get_by_student(self, student_id):
        """Get all tasks for a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Task_ID, Student_ID, Task_Title, Due_Date, Priority, Status FROM [Task] WHERE Student_ID = ?", (student_id,))
            rows = cursor.fetchall()
            tasks = []
            for row in rows:
                # Handle Due_Date - convert to datetime if it's a string or keep as datetime
                due_date = row[3]
                if due_date and isinstance(due_date, str):
                    try:
                        due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    except:
                        try:
                            due_date = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
                        except:
                            due_date = None
                
                tasks.append(Task(
                    Task_ID=row[0],
                    Student_ID=row[1],
                    Task_Title=row[2],
                    Due_Date=due_date,
                    Priority=row[4],
                    Status=row[5]
                ))
            return tasks
        finally:
            cursor.close()
            conn.close()
    
    def get_by_user_id(self, user_id):
        """Get all tasks for a user (requires join with Student table)"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.Task_ID, t.Student_ID, t.Task_Title, t.Due_Date, t.Priority, t.Status 
                FROM [Task] t
                JOIN [Student] s ON t.Student_ID = s.Student_ID
                WHERE s.User_ID = ?
            """, (user_id,))
            rows = cursor.fetchall()
            tasks = []
            for row in rows:
                # Handle Due_Date - convert to datetime if needed
                due_date = row[3]
                if due_date and isinstance(due_date, str):
                    try:
                        due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    except:
                        try:
                            due_date = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
                        except:
                            due_date = None
                
                tasks.append(Task(
                    Task_ID=row[0],
                    Student_ID=row[1],
                    Task_Title=row[2],
                    Due_Date=due_date,
                    Priority=row[4],
                    Status=row[5],
                    Completed=row[5] == 'Completed' if len(row) > 5 else False
                ))
            return tasks
        finally:
            cursor.close()
            conn.close()

    def create(self, task):
        """Create a new task"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO [Task] (Student_ID, Task_Title, Due_Date, Priority, Status) "
                "OUTPUT INSERTED.Task_ID "
                "VALUES (?, ?, ?, ?, ?)",
                (task.Student_ID, task.Task_Title, task.Due_Date, task.Priority, task.Status)
            )
            row = cursor.fetchone()
            if row:
                task.Task_ID = row[0]
            conn.commit()
            return task
        finally:
            cursor.close()
            conn.close()

    def update(self, task):
        """Update an existing task"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE [Task] SET Task_Title = ?, Due_Date = ?, Priority = ?, Status = ? WHERE Task_ID = ?",
                (task.Task_Title, task.Due_Date, task.Priority, task.Status, task.Task_ID)
            )
            conn.commit()
            return task
        finally:
            cursor.close()
            conn.close()

    def delete(self, task_id):
        """Delete a task by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [Task] WHERE Task_ID = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()


