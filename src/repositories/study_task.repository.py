from core.db_singleton import DatabaseConnection
from models.study_task import StudyTask
from datetime import datetime


class StudyTaskRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all study tasks"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Task_ID, Plan_ID, Parent_Task_ID, Task_Title, Description, 
                       Estimated_Hours, Actual_Hours, Due_Date, Priority, Status, 
                       Suggested_Resources, Created_At 
                FROM StudyTask
            """)
            rows = cursor.fetchall()
            tasks = []
            for row in rows:
                tasks.append(self._row_to_task(row))
            return tasks
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, task_id):
        """Get study task by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Task_ID, Plan_ID, Parent_Task_ID, Task_Title, Description, 
                       Estimated_Hours, Actual_Hours, Due_Date, Priority, Status, 
                       Suggested_Resources, Created_At 
                FROM StudyTask 
                WHERE Task_ID = ?
            """, (task_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_task(row)
            return None
        finally:
            cursor.close()
            conn.close()

    def get_by_plan(self, plan_id):
        """Get all tasks for a study plan"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Task_ID, Plan_ID, Parent_Task_ID, Task_Title, Description, 
                       Estimated_Hours, Actual_Hours, Due_Date, Priority, Status, 
                       Suggested_Resources, Created_At 
                FROM StudyTask 
                WHERE Plan_ID = ?
                ORDER BY Due_Date ASC, Priority DESC
            """, (plan_id,))
            rows = cursor.fetchall()
            tasks = []
            for row in rows:
                tasks.append(self._row_to_task(row))
            return tasks
        finally:
            cursor.close()
            conn.close()

    def get_subtasks(self, parent_task_id):
        """Get all subtasks for a parent task"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Task_ID, Plan_ID, Parent_Task_ID, Task_Title, Description, 
                       Estimated_Hours, Actual_Hours, Due_Date, Priority, Status, 
                       Suggested_Resources, Created_At 
                FROM StudyTask 
                WHERE Parent_Task_ID = ?
                ORDER BY Created_At ASC
            """, (parent_task_id,))
            rows = cursor.fetchall()
            tasks = []
            for row in rows:
                tasks.append(self._row_to_task(row))
            return tasks
        finally:
            cursor.close()
            conn.close()

    def get_pending_tasks(self, plan_id):
        """Get pending tasks for a study plan"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Task_ID, Plan_ID, Parent_Task_ID, Task_Title, Description, 
                       Estimated_Hours, Actual_Hours, Due_Date, Priority, Status, 
                       Suggested_Resources, Created_At 
                FROM StudyTask 
                WHERE Plan_ID = ? AND Status = 'pending'
                ORDER BY Due_Date ASC, Priority DESC
            """, (plan_id,))
            rows = cursor.fetchall()
            tasks = []
            for row in rows:
                tasks.append(self._row_to_task(row))
            return tasks
        finally:
            cursor.close()
            conn.close()

    def create(self, task):
        """Create a new study task"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO StudyTask (Plan_ID, Parent_Task_ID, Task_Title, Description, 
                                       Estimated_Hours, Actual_Hours, Due_Date, Priority, 
                                       Status, Suggested_Resources) 
                OUTPUT INSERTED.Task_ID 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (task.Plan_ID, task.Parent_Task_ID, task.Task_Title, task.Description,
                  task.Estimated_Hours, task.Actual_Hours, task.Due_Date, task.Priority,
                  task.Status, task.Suggested_Resources))
            row = cursor.fetchone()
            if row:
                task.Task_ID = row[0]
            conn.commit()
            return task
        finally:
            cursor.close()
            conn.close()

    def update(self, task):
        """Update an existing study task"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE StudyTask 
                SET Task_Title = ?, Description = ?, Estimated_Hours = ?, 
                    Actual_Hours = ?, Due_Date = ?, Priority = ?, Status = ?, 
                    Suggested_Resources = ?, Parent_Task_ID = ?
                WHERE Task_ID = ?
            """, (task.Task_Title, task.Description, task.Estimated_Hours,
                  task.Actual_Hours, task.Due_Date, task.Priority, task.Status,
                  task.Suggested_Resources, task.Parent_Task_ID, task.Task_ID))
            conn.commit()
            return task
        finally:
            cursor.close()
            conn.close()

    def update_status(self, task_id, status):
        """Update task status"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE StudyTask 
                SET Status = ?
                WHERE Task_ID = ?
            """, (status, task_id))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    def update_actual_hours(self, task_id, actual_hours):
        """Update actual hours spent on task"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE StudyTask 
                SET Actual_Hours = ?
                WHERE Task_ID = ?
            """, (actual_hours, task_id))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    def delete(self, task_id):
        """Delete a study task by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            # First delete all subtasks
            cursor.execute("DELETE FROM StudyTask WHERE Parent_Task_ID = ?", (task_id,))
            # Then delete the task itself
            cursor.execute("DELETE FROM StudyTask WHERE Task_ID = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def _row_to_task(self, row):
        """Convert database row to StudyTask object"""
        # Handle Due_Date - convert to datetime if needed
        due_date = row[7]
        if due_date and isinstance(due_date, str):
            try:
                due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except:
                try:
                    due_date = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
                except:
                    due_date = None
        
        return StudyTask(
            Task_ID=row[0],
            Plan_ID=row[1],
            Parent_Task_ID=row[2],
            Task_Title=row[3],
            Description=row[4],
            Estimated_Hours=row[5],
            Actual_Hours=row[6],
            Due_Date=due_date,
            Priority=row[8],
            Status=row[9],
            Suggested_Resources=row[10],
            Created_At=row[11]
        )
