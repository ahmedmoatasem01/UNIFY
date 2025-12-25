"""
Study Plan Repository
Handles database operations for study plans
"""
from models.study_plan import StudyPlan
from core.db_singleton import DatabaseConnection
from datetime import datetime, date


class StudyPlanRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()
    
    def create_table(self):
        """Create StudyPlan table if it doesn't exist"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[StudyPlan]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE StudyPlan (
                        Plan_ID INT IDENTITY(1,1) PRIMARY KEY,
                        Student_ID INT NOT NULL,
                        Course_ID INT,
                        Plan_Name NVARCHAR(255) NOT NULL,
                        Start_Date DATE NOT NULL,
                        End_Date DATE NOT NULL,
                        Status NVARCHAR(20) CHECK (Status IN ('active', 'paused', 'completed', 'archived')) DEFAULT 'active',
                        Completion_Percentage DECIMAL(5,2) DEFAULT 0,
                        Created_At DATETIME DEFAULT GETDATE(),
                        FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
                        FOREIGN KEY (Course_ID) REFERENCES Course(Course_ID)
                    )
                END
            """)
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def create(self, plan):
        """Create a new study plan"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO StudyPlan (Student_ID, Course_ID, Plan_Name, Start_Date, End_Date, Status, Completion_Percentage, Created_At)
                OUTPUT INSERTED.Plan_ID
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plan.Student_ID,
                plan.Course_ID,
                plan.Plan_Name,
                plan.Start_Date,
                plan.End_Date,
                plan.Status,
                plan.Completion_Percentage,
                plan.Created_At
            ))
            row = cursor.fetchone()
            if row:
                plan.Plan_ID = row[0]
            conn.commit()
            return plan
        finally:
            cursor.close()
            conn.close()
    
    def get_by_id(self, plan_id):
        """Get study plan by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Plan_ID, Student_ID, Course_ID, Plan_Name, Start_Date, End_Date, 
                       Status, Completion_Percentage, Created_At
                FROM StudyPlan WHERE Plan_ID = ?
            """, (plan_id,))
            row = cursor.fetchone()
            if row:
                return self._map_to_object(row)
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_by_student(self, student_id):
        """Get all study plans for a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Plan_ID, Student_ID, Course_ID, Plan_Name, Start_Date, End_Date, 
                       Status, Completion_Percentage, Created_At
                FROM StudyPlan WHERE Student_ID = ? ORDER BY Created_At DESC
            """, (student_id,))
            rows = cursor.fetchall()
            return [self._map_to_object(row) for row in rows] if rows else []
        finally:
            cursor.close()
            conn.close()
    
    def update(self, plan):
        """Update a study plan"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE StudyPlan 
                SET Plan_Name = ?, Start_Date = ?, End_Date = ?, Status = ?, Completion_Percentage = ?
                WHERE Plan_ID = ?
            """, (
                plan.Plan_Name,
                plan.Start_Date,
                plan.End_Date,
                plan.Status,
                plan.Completion_Percentage,
                plan.Plan_ID
            ))
            conn.commit()
            return plan
        finally:
            cursor.close()
            conn.close()
    
    def delete(self, plan_id):
        """Delete a study plan"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM StudyPlan WHERE Plan_ID = ?", (plan_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    
    def _map_to_object(self, row):
        """Map database row to StudyPlan object"""
        if not row:
            return None
        return StudyPlan(
            Plan_ID=row[0],
            Student_ID=row[1],
            Course_ID=row[2],
            Plan_Name=row[3],
            Start_Date=row[4],
            End_Date=row[5],
            Status=row[6],
            Completion_Percentage=row[7] if row[7] else 0.0,
            Created_At=row[8]
        )

