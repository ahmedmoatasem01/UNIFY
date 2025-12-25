"""
Assignment Repository
Handles database operations for assignments
"""
from core.db_singleton import DatabaseConnection
from models.assignment import Assignment
from datetime import datetime


class AssignmentRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()
    
    def create_table(self):
        """Create the Assignment table if it doesn't exist"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Assignment]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE [Assignment] (
                        Assignment_ID INT IDENTITY(1,1) PRIMARY KEY,
                        Course_ID INT NOT NULL,
                        Title NVARCHAR(255) NOT NULL,
                        Description NVARCHAR(MAX),
                        Instructions NVARCHAR(MAX),
                        Due_Date DATETIME NOT NULL,
                        Max_Score DECIMAL(5,2) DEFAULT 100,
                        Assignment_Type NVARCHAR(50),
                        Allowed_File_Types NVARCHAR(200),
                        Max_File_Size_MB INT DEFAULT 10,
                        Created_By INT,
                        Created_At DATETIME DEFAULT GETDATE(),
                        Solution_Path NVARCHAR(500),
                        Solution_File_Name NVARCHAR(255),
                        Correct_Answer NVARCHAR(MAX),
                        Is_Auto_Graded BIT DEFAULT 0,
                        FOREIGN KEY (Course_ID) REFERENCES Course(Course_ID),
                        FOREIGN KEY (Created_By) REFERENCES Instructor(Instructor_ID)
                    )
                END
            """)
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def get_all(self):
        """Get all assignments"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Assignment_ID, Course_ID, Title, Description, Instructions, Due_Date, 
                       Max_Score, Assignment_Type, Allowed_File_Types, Max_File_Size_MB,
                       Created_By, Created_At, Solution_Path, Solution_File_Name, Correct_Answer, Is_Auto_Graded
                FROM [Assignment]
                ORDER BY Created_At DESC
            """)
            rows = cursor.fetchall()
            assignments = []
            for row in rows:
                assignments.append(self._row_to_assignment(row))
            return assignments
        finally:
            cursor.close()
            conn.close()
    
    def get_by_id(self, assignment_id):
        """Get assignment by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Assignment_ID, Course_ID, Title, Description, Instructions, Due_Date, 
                       Max_Score, Assignment_Type, Allowed_File_Types, Max_File_Size_MB,
                       Created_By, Created_At, Solution_Path, Solution_File_Name, Correct_Answer, Is_Auto_Graded
                FROM [Assignment]
                WHERE Assignment_ID = ?
            """, (assignment_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_assignment(row)
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_by_course(self, course_id):
        """Get all assignments for a course"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Assignment_ID, Course_ID, Title, Description, Instructions, Due_Date, 
                       Max_Score, Assignment_Type, Allowed_File_Types, Max_File_Size_MB,
                       Created_By, Created_At, Solution_Path, Solution_File_Name, Correct_Answer, Is_Auto_Graded
                FROM [Assignment]
                WHERE Course_ID = ?
                ORDER BY Due_Date ASC
            """, (course_id,))
            rows = cursor.fetchall()
            assignments = []
            for row in rows:
                assignments.append(self._row_to_assignment(row))
            return assignments
        finally:
            cursor.close()
            conn.close()
    
    def get_by_creator(self, instructor_id):
        """Get all assignments created by an instructor/TA"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Assignment_ID, Course_ID, Title, Description, Instructions, Due_Date, 
                       Max_Score, Assignment_Type, Allowed_File_Types, Max_File_Size_MB,
                       Created_By, Created_At, Solution_Path, Solution_File_Name, Correct_Answer, Is_Auto_Graded
                FROM [Assignment]
                WHERE Created_By = ?
                ORDER BY Created_At DESC
            """, (instructor_id,))
            rows = cursor.fetchall()
            assignments = []
            for row in rows:
                assignments.append(self._row_to_assignment(row))
            return assignments
        finally:
            cursor.close()
            conn.close()
    
    def create(self, assignment):
        """Create a new assignment"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO [Assignment] (Course_ID, Title, Description, Instructions, Due_Date, 
                    Max_Score, Assignment_Type, Allowed_File_Types, Max_File_Size_MB, Created_By, 
                    Created_At, Solution_Path, Solution_File_Name, Correct_Answer, Is_Auto_Graded)
                OUTPUT INSERTED.Assignment_ID
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assignment.Course_ID, assignment.Title, assignment.Description, assignment.Instructions,
                assignment.Due_Date, assignment.Max_Score, assignment.Assignment_Type,
                assignment.Allowed_File_Types, assignment.Max_File_Size_MB, assignment.Created_By,
                assignment.Created_At, assignment.Solution_Path, assignment.Solution_File_Name,
                assignment.Correct_Answer, assignment.Is_Auto_Graded
            ))
            row = cursor.fetchone()
            if row:
                assignment.Assignment_ID = row[0]
            conn.commit()
            return assignment
        finally:
            cursor.close()
            conn.close()
    
    def update(self, assignment):
        """Update an assignment"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE [Assignment]
                SET Course_ID = ?, Title = ?, Description = ?, Instructions = ?, Due_Date = ?,
                    Max_Score = ?, Assignment_Type = ?, Allowed_File_Types = ?, Max_File_Size_MB = ?,
                    Solution_Path = ?, Solution_File_Name = ?, Correct_Answer = ?, Is_Auto_Graded = ?
                WHERE Assignment_ID = ?
            """, (
                assignment.Course_ID, assignment.Title, assignment.Description, assignment.Instructions,
                assignment.Due_Date, assignment.Max_Score, assignment.Assignment_Type,
                assignment.Allowed_File_Types, assignment.Max_File_Size_MB,
                assignment.Solution_Path, assignment.Solution_File_Name, assignment.Correct_Answer,
                assignment.Is_Auto_Graded, assignment.Assignment_ID
            ))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    
    def delete(self, assignment_id):
        """Delete an assignment"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [Assignment] WHERE Assignment_ID = ?", (assignment_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    
    def _row_to_assignment(self, row):
        """Convert database row to Assignment object"""
        due_date = row[5]
        if isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        
        created_at = row[11]
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        return Assignment(
            Assignment_ID=row[0],
            Course_ID=row[1],
            Title=row[2],
            Description=row[3],
            Instructions=row[4],
            Due_Date=due_date,
            Max_Score=float(row[6]) if row[6] else 100.0,
            Assignment_Type=row[7],
            Allowed_File_Types=row[8],
            Max_File_Size_MB=row[9] if row[9] else 10,
            Created_By=row[10],
            Created_At=created_at,
            Solution_Path=row[12],
            Solution_File_Name=row[13],
            Correct_Answer=row[14],
            Is_Auto_Graded=bool(row[15]) if row[15] is not None else False
        )
