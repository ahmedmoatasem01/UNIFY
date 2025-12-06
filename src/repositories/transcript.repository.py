from core.db_singleton import DatabaseConnection
from models.transcript import Transcript


class TranscriptRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all transcripts"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Transcript_ID, Student_ID, GPA, PDF_Path, Issue_Date FROM Transcript")
            rows = cursor.fetchall()
            transcripts = []
            for row in rows:
                transcripts.append(Transcript(
                    Transcript_ID=row[0],
                    Student_ID=row[1],
                    GPA=row[2],
                    PDF_Path=row[3],
                    Issue_Date=row[4]
                ))
            return transcripts
        finally:
            conn.close()

    def get_by_id(self, transcript_id):
        """Get transcript by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Transcript_ID, Student_ID, GPA, PDF_Path, Issue_Date FROM Transcript WHERE Transcript_ID = ?", (transcript_id,))
            row = cursor.fetchone()
            if row:
                return Transcript(
                    Transcript_ID=row[0],
                    Student_ID=row[1],
                    GPA=row[2],
                    PDF_Path=row[3],
                    Issue_Date=row[4]
                )
            return None
        finally:
            conn.close()

    def get_by_student(self, student_id):
        """Get all transcripts for a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Transcript_ID, Student_ID, GPA, PDF_Path, Issue_Date FROM Transcript WHERE Student_ID = ?", (student_id,))
            rows = cursor.fetchall()
            transcripts = []
            for row in rows:
                transcripts.append(Transcript(
                    Transcript_ID=row[0],
                    Student_ID=row[1],
                    GPA=row[2],
                    PDF_Path=row[3],
                    Issue_Date=row[4]
                ))
            return transcripts
        finally:
            conn.close()

    def create(self, transcript):
        """Create a new transcript"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Transcript (Student_ID, GPA, PDF_Path, Issue_Date) OUTPUT INSERTED.Transcript_ID VALUES (?, ?, ?, ?)",
                (transcript.Student_ID, transcript.GPA, transcript.PDF_Path, transcript.Issue_Date)
            )
            transcript_id = cursor.fetchone()[0]
            conn.commit()
            transcript.Transcript_ID = transcript_id
            return transcript
        finally:
            conn.close()

    def update(self, transcript):
        """Update an existing transcript"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Transcript SET GPA = ?, PDF_Path = ?, Issue_Date = ? WHERE Transcript_ID = ?",
                (transcript.GPA, transcript.PDF_Path, transcript.Issue_Date, transcript.Transcript_ID)
            )
            conn.commit()
            return transcript
        finally:
            conn.close()

    def delete(self, transcript_id):
        """Delete a transcript by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Transcript WHERE Transcript_ID = ?", (transcript_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

