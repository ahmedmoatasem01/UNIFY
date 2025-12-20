from core.db_singleton import DatabaseConnection
from models.ai_note import AINote
import datetime

class AINoteRepository:
    def __init__(self):
        self.db = DatabaseConnection()

    def save_summary(self, student_id, filename, summary_text):
        """Insert summarized note into DB"""
        conn = self.db.get_connection()
        try:
            upload_date = datetime.datetime.now()

            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Note (Student_ID, Original_File, Summary_Text, Upload_Date)
                OUTPUT INSERTED.Note_ID
                VALUES (?, ?, ?, ?)
            """, (student_id, filename, summary_text, upload_date))

            note_id = cursor.fetchone()[0]
            conn.commit()

            return AINote(
                Note_ID=note_id,
                Student_ID=student_id,
                Original_File=filename,
                Summary_Text=summary_text,
                Upload_Date=upload_date
            )

        finally:
            conn.close()

    def get_by_id(self, note_id):
        """Get note by ID"""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Note_ID, Student_ID, Original_File, Summary_Text, Upload_Date
                FROM [Note]
                WHERE Note_ID = ?
            """, (note_id,))
            row = cursor.fetchone()
            if row:
                return AINote(
                    Note_ID=row[0],
                    Student_ID=row[1],
                    Original_File=row[2],
                    Summary_Text=row[3],
                    Upload_Date=row[4]
                )
            return None
        finally:
            conn.close()

    def get_by_student_id(self, student_id):
        """Get all notes for a student"""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Note_ID, Student_ID, Original_File, Summary_Text, Upload_Date
                FROM [Note]
                WHERE Student_ID = ?
                ORDER BY Upload_Date DESC
            """, (student_id,))
            rows = cursor.fetchall()
            notes = []
            for row in rows:
                notes.append(AINote(
                    Note_ID=row[0],
                    Student_ID=row[1],
                    Original_File=row[2],
                    Summary_Text=row[3],
                    Upload_Date=row[4]
                ))
            return notes
        finally:
            conn.close()

    def delete(self, note_id):
        """Delete a note by ID"""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [Note] WHERE Note_ID = ?", (note_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()