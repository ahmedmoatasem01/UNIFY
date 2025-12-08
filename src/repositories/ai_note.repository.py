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
