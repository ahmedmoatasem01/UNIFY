from core.db_singleton import DatabaseConnection
from models.study_plan import StudyPlan
from datetime import datetime, date


class StudyPlanRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all study plans"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Plan_ID, Student_ID, Course_ID, Plan_Name, Start_Date, End_Date, 
                       Status, Completion_Percentage, Created_At 
                FROM StudyPlan
            """)
            rows = cursor.fetchall()
            plans = []
            for row in rows:
                plans.append(StudyPlan(
                    Plan_ID=row[0],
                    Student_ID=row[1],
                    Course_ID=row[2],
                    Plan_Name=row[3],
                    Start_Date=row[4],
                    End_Date=row[5],
                    Status=row[6],
                    Completion_Percentage=row[7],
                    Created_At=row[8]
                ))
            return plans
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
                FROM StudyPlan 
                WHERE Plan_ID = ?
            """, (plan_id,))
            row = cursor.fetchone()
            if row:
                return StudyPlan(
                    Plan_ID=row[0],
                    Student_ID=row[1],
                    Course_ID=row[2],
                    Plan_Name=row[3],
                    Start_Date=row[4],
                    End_Date=row[5],
                    Status=row[6],
                    Completion_Percentage=row[7],
                    Created_At=row[8]
                )
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
                FROM StudyPlan 
                WHERE Student_ID = ?
                ORDER BY Created_At DESC
            """, (student_id,))
            rows = cursor.fetchall()
            plans = []
            for row in rows:
                plans.append(StudyPlan(
                    Plan_ID=row[0],
                    Student_ID=row[1],
                    Course_ID=row[2],
                    Plan_Name=row[3],
                    Start_Date=row[4],
                    End_Date=row[5],
                    Status=row[6],
                    Completion_Percentage=row[7],
                    Created_At=row[8]
                ))
            return plans
        finally:
            cursor.close()
            conn.close()

    def get_by_course(self, course_id):
        """Get all study plans for a course"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Plan_ID, Student_ID, Course_ID, Plan_Name, Start_Date, End_Date, 
                       Status, Completion_Percentage, Created_At 
                FROM StudyPlan 
                WHERE Course_ID = ?
                ORDER BY Created_At DESC
            """, (course_id,))
            rows = cursor.fetchall()
            plans = []
            for row in rows:
                plans.append(StudyPlan(
                    Plan_ID=row[0],
                    Student_ID=row[1],
                    Course_ID=row[2],
                    Plan_Name=row[3],
                    Start_Date=row[4],
                    End_Date=row[5],
                    Status=row[6],
                    Completion_Percentage=row[7],
                    Created_At=row[8]
                ))
            return plans
        finally:
            cursor.close()
            conn.close()

    def get_active_plans(self, student_id):
        """Get active study plans for a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Plan_ID, Student_ID, Course_ID, Plan_Name, Start_Date, End_Date, 
                       Status, Completion_Percentage, Created_At 
                FROM StudyPlan 
                WHERE Student_ID = ? AND Status = 'active'
                ORDER BY Created_At DESC
            """, (student_id,))
            rows = cursor.fetchall()
            plans = []
            for row in rows:
                plans.append(StudyPlan(
                    Plan_ID=row[0],
                    Student_ID=row[1],
                    Course_ID=row[2],
                    Plan_Name=row[3],
                    Start_Date=row[4],
                    End_Date=row[5],
                    Status=row[6],
                    Completion_Percentage=row[7],
                    Created_At=row[8]
                ))
            return plans
        finally:
            cursor.close()
            conn.close()

    def create(self, plan):
        """Create a new study plan"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO StudyPlan (Student_ID, Course_ID, Plan_Name, Start_Date, End_Date, 
                                       Status, Completion_Percentage) 
                OUTPUT INSERTED.Plan_ID 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (plan.Student_ID, plan.Course_ID, plan.Plan_Name, plan.Start_Date, 
                  plan.End_Date, plan.Status, plan.Completion_Percentage))
            row = cursor.fetchone()
            if row:
                plan.Plan_ID = row[0]
            conn.commit()
            return plan
        finally:
            cursor.close()
            conn.close()

    def update(self, plan):
        """Update an existing study plan"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE StudyPlan 
                SET Plan_Name = ?, Start_Date = ?, End_Date = ?, Status = ?, 
                    Completion_Percentage = ?, Course_ID = ?
                WHERE Plan_ID = ?
            """, (plan.Plan_Name, plan.Start_Date, plan.End_Date, plan.Status, 
                  plan.Completion_Percentage, plan.Course_ID, plan.Plan_ID))
            conn.commit()
            return plan
        finally:
            cursor.close()
            conn.close()

    def update_completion_percentage(self, plan_id, percentage):
        """Update completion percentage of a study plan"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE StudyPlan 
                SET Completion_Percentage = ?
                WHERE Plan_ID = ?
            """, (percentage, plan_id))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    def delete(self, plan_id):
        """Delete a study plan by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM StudyPlan WHERE Plan_ID = ?", (plan_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
