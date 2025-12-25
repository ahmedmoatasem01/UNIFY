"""
GradingSuggestion Repository
Handles database operations for GradingSuggestion model
"""
from core.db_singleton import DatabaseConnection
from models.grading_suggestion import GradingSuggestion
from datetime import datetime
from typing import List, Optional
import json


class GradingSuggestionRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()
    
    def create_table(self):
        """Create the GradingSuggestion table if it doesn't exist"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[GradingSuggestion]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE [GradingSuggestion] (
                        Suggestion_ID INT IDENTITY(1,1) PRIMARY KEY,
                        Submission_ID INT NOT NULL,
                        Suggested_Grade DECIMAL(5,2),
                        Confidence_Score DECIMAL(3,2),
                        Rubric_Scores NVARCHAR(MAX),
                        Feedback_Suggestions NVARCHAR(MAX),
                        Flagged_For_Review BIT DEFAULT 0,
                        Flag_Reason NVARCHAR(500),
                        Generated_At DATETIME DEFAULT GETDATE(),
                        Accepted BIT,
                        FOREIGN KEY (Submission_ID) REFERENCES Assignment_Submission(Submission_ID)
                    )
                END
            """)
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def get_by_id(self, suggestion_id: int) -> Optional[GradingSuggestion]:
        """Get grading suggestion by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Suggestion_ID, Submission_ID, Suggested_Grade, Confidence_Score,
                       Rubric_Scores, Feedback_Suggestions, Flagged_For_Review, Flag_Reason,
                       Generated_At, Accepted
                FROM [GradingSuggestion]
                WHERE Suggestion_ID = ?
            """, (suggestion_id,))
            row = cursor.fetchone()
            return self._row_to_suggestion(row) if row else None
        finally:
            cursor.close()
            conn.close()
    
    def get_by_submission(self, submission_id: int) -> List[GradingSuggestion]:
        """Get all grading suggestions for a submission"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Suggestion_ID, Submission_ID, Suggested_Grade, Confidence_Score,
                       Rubric_Scores, Feedback_Suggestions, Flagged_For_Review, Flag_Reason,
                       Generated_At, Accepted
                FROM [GradingSuggestion]
                WHERE Submission_ID = ?
                ORDER BY Generated_At DESC
            """, (submission_id,))
            rows = cursor.fetchall()
            return [self._row_to_suggestion(row) for row in rows]
        finally:
            cursor.close()
            conn.close()
    
    def create(self, suggestion: GradingSuggestion) -> GradingSuggestion:
        """Create a new grading suggestion"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO [GradingSuggestion] (Submission_ID, Suggested_Grade, Confidence_Score,
                                                 Rubric_Scores, Feedback_Suggestions, Flagged_For_Review,
                                                 Flag_Reason, Generated_At, Accepted)
                OUTPUT INSERTED.Suggestion_ID
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                suggestion.Submission_ID,
                suggestion.Suggested_Grade,
                suggestion.Confidence_Score,
                suggestion.Rubric_Scores,
                suggestion.Feedback_Suggestions,
                1 if suggestion.Flagged_For_Review else 0,
                suggestion.Flag_Reason,
                suggestion.Generated_At,
                suggestion.Accepted
            ))
            suggestion.Suggestion_ID = cursor.fetchone()[0]
            conn.commit()
            return suggestion
        finally:
            cursor.close()
            conn.close()
    
    def update(self, suggestion: GradingSuggestion) -> GradingSuggestion:
        """Update a grading suggestion"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE [GradingSuggestion]
                SET Suggested_Grade = ?, Confidence_Score = ?, Rubric_Scores = ?,
                    Feedback_Suggestions = ?, Flagged_For_Review = ?, Flag_Reason = ?,
                    Accepted = ?
                WHERE Suggestion_ID = ?
            """, (
                suggestion.Suggested_Grade,
                suggestion.Confidence_Score,
                suggestion.Rubric_Scores,
                suggestion.Feedback_Suggestions,
                1 if suggestion.Flagged_For_Review else 0,
                suggestion.Flag_Reason,
                suggestion.Accepted,
                suggestion.Suggestion_ID
            ))
            conn.commit()
            return suggestion
        finally:
            cursor.close()
            conn.close()
    
    def delete(self, suggestion_id: int) -> bool:
        """Delete a grading suggestion"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [GradingSuggestion] WHERE Suggestion_ID = ?", (suggestion_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    
    def _row_to_suggestion(self, row: tuple) -> GradingSuggestion:
        """Convert database row to GradingSuggestion object"""
        if not row:
            return None
        
        return GradingSuggestion(
            Suggestion_ID=row[0],
            Submission_ID=row[1],
            Suggested_Grade=float(row[2]) if row[2] is not None else None,
            Confidence_Score=float(row[3]) if row[3] is not None else None,
            Rubric_Scores=row[4],
            Feedback_Suggestions=row[5],
            Flagged_For_Review=bool(row[6]) if row[6] is not None else False,
            Flag_Reason=row[7],
            Generated_At=row[8],
            Accepted=bool(row[9]) if row[9] is not None else None
        )

