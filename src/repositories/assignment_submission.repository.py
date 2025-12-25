"""
Assignment Submission Repository
Handles database operations for assignment submissions
"""
from core.db_singleton import DatabaseConnection
from models.assignment_submission import AssignmentSubmission
from datetime import datetime


class AssignmentSubmissionRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()
    
    def create_table(self):
        """Create the Assignment_Submission table if it doesn't exist"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Assignment_Submission]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE [Assignment_Submission] (
                        Submission_ID INT IDENTITY(1,1) PRIMARY KEY,
                        Assignment_ID INT NOT NULL,
                        Student_ID INT NOT NULL,
                        File_Path NVARCHAR(500),
                        File_Name NVARCHAR(255),
                        Submission_Text NVARCHAR(MAX),
                        Submitted_At DATETIME DEFAULT GETDATE(),
                        Status NVARCHAR(20) CHECK (Status IN ('submitted', 'late', 'graded', 'review_requested')) DEFAULT 'submitted',
                        Grade DECIMAL(5,2),
                        Feedback NVARCHAR(MAX),
                        Graded_By INT,
                        Graded_At DATETIME,
                        Review_Requested BIT DEFAULT 0,
                        Review_Comment NVARCHAR(MAX),
                        Is_AI_Graded BIT DEFAULT 0,
                        FOREIGN KEY (Assignment_ID) REFERENCES Assignment(Assignment_ID),
                        FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
                        FOREIGN KEY (Graded_By) REFERENCES Instructor(Instructor_ID) ON DELETE SET NULL
                    )
                END
            """)
            
            # Add new columns if they don't exist (for existing tables)
            try:
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[Assignment_Submission]') AND name = 'Review_Requested')
                    BEGIN
                        ALTER TABLE [Assignment_Submission] ADD Review_Requested BIT DEFAULT 0
                    END
                """)
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[Assignment_Submission]') AND name = 'Review_Comment')
                    BEGIN
                        ALTER TABLE [Assignment_Submission] ADD Review_Comment NVARCHAR(MAX)
                    END
                """)
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[Assignment_Submission]') AND name = 'Is_AI_Graded')
                    BEGIN
                        ALTER TABLE [Assignment_Submission] ADD Is_AI_Graded BIT DEFAULT 0
                    END
                """)
                
                # Update CHECK constraint for Status column to include 'review_requested'
                # Find and drop existing Status check constraints
                cursor.execute("""
                    DECLARE @ConstraintName NVARCHAR(200)
                    DECLARE @SQL NVARCHAR(MAX)
                    
                    -- Find Status column constraints by checking definitions that include Status column values
                    DECLARE constraint_cursor CURSOR FOR
                    SELECT cc.name 
                    FROM sys.check_constraints cc
                    INNER JOIN sys.columns c ON c.object_id = cc.parent_object_id AND c.column_id = cc.parent_column_id
                    WHERE cc.parent_object_id = OBJECT_ID(N'[dbo].[Assignment_Submission]')
                    AND c.name = 'Status'
                    AND (cc.definition LIKE '%submitted%' OR cc.definition LIKE '%graded%' OR cc.definition LIKE '%late%')
                    
                    OPEN constraint_cursor
                    FETCH NEXT FROM constraint_cursor INTO @ConstraintName
                    
                    WHILE @@FETCH_STATUS = 0
                    BEGIN
                        SET @SQL = 'ALTER TABLE [dbo].[Assignment_Submission] DROP CONSTRAINT [' + @ConstraintName + ']'
                        EXEC sp_executesql @SQL
                        FETCH NEXT FROM constraint_cursor INTO @ConstraintName
                    END
                    
                    CLOSE constraint_cursor
                    DEALLOCATE constraint_cursor
                """)
                
                # Add new constraint with all allowed values including 'review_requested'
                cursor.execute("""
                    IF NOT EXISTS (
                        SELECT * FROM sys.check_constraints 
                        WHERE name = 'CK_Assignment_Submission_Status' 
                        AND parent_object_id = OBJECT_ID(N'[dbo].[Assignment_Submission]')
                    )
                    BEGIN
                        ALTER TABLE [Assignment_Submission]
                        ADD CONSTRAINT CK_Assignment_Submission_Status 
                        CHECK (Status IN ('submitted', 'late', 'graded', 'review_requested'))
                    END
                """)
            except Exception as e:
                # Log error but continue - constraint might already be updated
                print(f"Warning: Could not update Status constraint: {e}")
                pass
            
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def get_by_id(self, submission_id):
        """Get submission by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Submission_ID, Assignment_ID, Student_ID, File_Path, File_Name, Submission_Text,
                       Submitted_At, Status, Grade, Feedback, Graded_By, Graded_At,
                       Review_Requested, Review_Comment, Is_AI_Graded
                FROM [Assignment_Submission]
                WHERE Submission_ID = ?
            """, (submission_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_submission(row)
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_by_assignment(self, assignment_id):
        """Get all submissions for an assignment"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Submission_ID, Assignment_ID, Student_ID, File_Path, File_Name, Submission_Text,
                       Submitted_At, Status, Grade, Feedback, Graded_By, Graded_At,
                       Review_Requested, Review_Comment, Is_AI_Graded
                FROM [Assignment_Submission]
                WHERE Assignment_ID = ?
                ORDER BY Submitted_At DESC
            """, (assignment_id,))
            rows = cursor.fetchall()
            submissions = []
            for row in rows:
                submissions.append(self._row_to_submission(row))
            return submissions
        finally:
            cursor.close()
            conn.close()
    
    def get_by_student(self, student_id):
        """Get all submissions by a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Submission_ID, Assignment_ID, Student_ID, File_Path, File_Name, Submission_Text,
                       Submitted_At, Status, Grade, Feedback, Graded_By, Graded_At,
                       Review_Requested, Review_Comment, Is_AI_Graded
                FROM [Assignment_Submission]
                WHERE Student_ID = ?
                ORDER BY Submitted_At DESC
            """, (student_id,))
            rows = cursor.fetchall()
            submissions = []
            for row in rows:
                submissions.append(self._row_to_submission(row))
            return submissions
        finally:
            cursor.close()
            conn.close()
    
    def get_by_student_and_assignment(self, student_id, assignment_id):
        """Get a student's submission for a specific assignment"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP 1 Submission_ID, Assignment_ID, Student_ID, File_Path, File_Name, Submission_Text,
                       Submitted_At, Status, Grade, Feedback, Graded_By, Graded_At,
                       Review_Requested, Review_Comment, Is_AI_Graded
                FROM [Assignment_Submission]
                WHERE Student_ID = ? AND Assignment_ID = ?
                ORDER BY Submitted_At DESC
            """, (student_id, assignment_id))
            row = cursor.fetchone()
            if row:
                return self._row_to_submission(row)
            return None
        finally:
            cursor.close()
            conn.close()
    
    def create(self, submission):
        """Create a new submission"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO [Assignment_Submission] (Assignment_ID, Student_ID, File_Path, File_Name, 
                    Submission_Text, Submitted_At, Status, Grade, Feedback, Graded_By, Graded_At)
                OUTPUT INSERTED.Submission_ID
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                submission.Assignment_ID, submission.Student_ID, submission.File_Path,
                submission.File_Name, submission.Submission_Text, submission.Submitted_At,
                submission.Status, submission.Grade, submission.Feedback,
                submission.Graded_By, submission.Graded_At
            ))
            row = cursor.fetchone()
            if row:
                submission.Submission_ID = row[0]
            conn.commit()
            return submission
        finally:
            cursor.close()
            conn.close()
    
    def update(self, submission):
        """Update a submission"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE [Assignment_Submission]
                SET File_Path = ?, File_Name = ?, Submission_Text = ?, Status = ?,
                    Grade = ?, Feedback = ?, Graded_By = ?, Graded_At = ?,
                    Review_Requested = ?, Review_Comment = ?, Is_AI_Graded = ?
                WHERE Submission_ID = ?
            """, (
                submission.File_Path, submission.File_Name, submission.Submission_Text,
                submission.Status, submission.Grade, submission.Feedback,
                submission.Graded_By, submission.Graded_At,
                submission.Review_Requested if hasattr(submission, 'Review_Requested') else False,
                submission.Review_Comment if hasattr(submission, 'Review_Comment') else None,
                submission.Is_AI_Graded if hasattr(submission, 'Is_AI_Graded') else False,
                submission.Submission_ID
            ))
            conn.commit()
            if cursor.rowcount > 0:
                # Return the updated submission object
                return submission
            return None
        finally:
            cursor.close()
            conn.close()
    
    def _row_to_submission(self, row):
        """Convert database row to AssignmentSubmission object"""
        submitted_at = row[6]
        if submitted_at and isinstance(submitted_at, str):
            submitted_at = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
        
        graded_at = row[11]
        if graded_at and isinstance(graded_at, str):
            graded_at = datetime.fromisoformat(graded_at.replace('Z', '+00:00'))
        
        # Handle old rows that don't have the new fields
        review_requested = row[12] if len(row) > 12 else False
        review_comment = row[13] if len(row) > 13 else None
        is_ai_graded = row[14] if len(row) > 14 else False
        
        return AssignmentSubmission(
            Submission_ID=row[0],
            Assignment_ID=row[1],
            Student_ID=row[2],
            File_Path=row[3],
            File_Name=row[4],
            Submission_Text=row[5],
            Submitted_At=submitted_at,
            Status=row[7],
            Grade=float(row[8]) if row[8] is not None else None,
            Feedback=row[9],
            Graded_By=row[10],
            Graded_At=graded_at,
            Review_Requested=bool(review_requested),
            Review_Comment=review_comment,
            Is_AI_Graded=bool(is_ai_graded)
        )
