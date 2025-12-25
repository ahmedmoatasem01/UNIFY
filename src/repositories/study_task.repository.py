"""
Study Task Repository
Handles database operations for study tasks
"""
from models.study_task import StudyTask
from core.db_singleton import DatabaseConnection
from datetime import datetime


class StudyTaskRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()
    
    def create_table(self):
        """Create StudyTask table if it doesn't exist"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[StudyTask]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE StudyTask (
                        Task_ID INT IDENTITY(1,1) PRIMARY KEY,
                        Plan_ID INT NOT NULL,
                        Parent_Task_ID INT,
                        Task_Title NVARCHAR(255) NOT NULL,
                        Description NVARCHAR(MAX),
                        Estimated_Hours DECIMAL(4,1),
                        Actual_Hours DECIMAL(4,1),
                        Due_Date DATETIME,
                        Priority NVARCHAR(10) CHECK (Priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
                        Status NVARCHAR(20) CHECK (Status IN ('pending', 'in_progress', 'completed', 'skipped')) DEFAULT 'pending',
                        Suggested_Resources NVARCHAR(MAX),
                        Created_At DATETIME DEFAULT GETDATE(),
                        FOREIGN KEY (Plan_ID) REFERENCES StudyPlan(Plan_ID) ON DELETE CASCADE,
                        FOREIGN KEY (Parent_Task_ID) REFERENCES StudyTask(Task_ID)
                    )
                END
            """)
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def create(self, task):
        """Create a new study task"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO StudyTask (Plan_ID, Parent_Task_ID, Task_Title, Description, Estimated_Hours, 
                                     Actual_Hours, Due_Date, Priority, Status, Suggested_Resources, Created_At)
                OUTPUT INSERTED.Task_ID
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.Plan_ID,
                task.Parent_Task_ID,
                task.Task_Title,
                task.Description,
                task.Estimated_Hours,
                task.Actual_Hours,
                task.Due_Date,
                task.Priority,
                task.Status,
                task.Suggested_Resources,
                task.Created_At
            ))
            row = cursor.fetchone()
            if row:
                task.Task_ID = row[0]
            conn.commit()
            return task
        finally:
            cursor.close()
            conn.close()
    
    def get_by_id(self, task_id):
        """Get study task by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Task_ID, Plan_ID, Parent_Task_ID, Task_Title, Description, Estimated_Hours,
                       Actual_Hours, Due_Date, Priority, Status, Suggested_Resources, Created_At
                FROM StudyTask WHERE Task_ID = ?
            """, (task_id,))
            row = cursor.fetchone()
            if row:
                return self._map_to_object(row)
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
                SELECT Task_ID, Plan_ID, Parent_Task_ID, Task_Title, Description, Estimated_Hours,
                       Actual_Hours, Due_Date, Priority, Status, Suggested_Resources, Created_At
                FROM StudyTask WHERE Plan_ID = ? ORDER BY Due_Date ASC, Priority DESC
            """, (plan_id,))
            rows = cursor.fetchall()
            return [self._map_to_object(row) for row in rows] if rows else []
        finally:
            cursor.close()
            conn.close()
    
    def update(self, task):
        """Update a study task"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE StudyTask 
                SET Task_Title = ?, Description = ?, Estimated_Hours = ?, Actual_Hours = ?,
                    Due_Date = ?, Priority = ?, Status = ?, Suggested_Resources = ?
                WHERE Task_ID = ?
            """, (
                task.Task_Title,
                task.Description,
                task.Estimated_Hours,
                task.Actual_Hours,
                task.Due_Date,
                task.Priority,
                task.Status,
                task.Suggested_Resources,
                task.Task_ID
            ))
            conn.commit()
            return task
        finally:
            cursor.close()
            conn.close()
    
    def delete(self, task_id):
        """Delete a study task"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM StudyTask WHERE Task_ID = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    
    def _map_to_object(self, row):
        """Map database row to StudyTask object"""
        if not row:
            return None
        return StudyTask(
            Task_ID=row[0],
            Plan_ID=row[1],
            Parent_Task_ID=row[2],
            Task_Title=row[3],
            Description=row[4],
            Estimated_Hours=row[5],
            Actual_Hours=row[6],
            Due_Date=row[7],
            Priority=row[8],
            Status=row[9],
            Suggested_Resources=row[10],
            Created_At=row[11]
        )

