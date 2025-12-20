from core.db_singleton import DatabaseConnection
from models.note import Note


class NoteRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all notes"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Note_ID, Student_ID, Original_File, Summary_Text, Upload_Date FROM Note")
            rows = cursor.fetchall()
            notes = []
            for row in rows:
                notes.append(Note(
                    Note_ID=row[0],
                    Student_ID=row[1],
                    Original_File=row[2],
                    Summary_Text=row[3],
                    Upload_Date=row[4]
                ))
            return notes
        finally:
            conn.close()

    def get_by_id(self, note_id):
        """Get note by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Note_ID, Student_ID, Original_File, Summary_Text, Upload_Date FROM Note WHERE Note_ID = ?", (note_id,))
            row = cursor.fetchone()
            if row:
                return Note(
                    Note_ID=row[0],
                    Student_ID=row[1],
                    Original_File=row[2],
                    Summary_Text=row[3],
                    Upload_Date=row[4]
                )
            return None
        finally:
            conn.close()

    

    def get_by_student(self, student_id):
        """Get all notes for a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Note_ID, Student_ID, Original_File, Summary_Text, Upload_Date FROM Note WHERE Student_ID = ?", (student_id,))
            rows = cursor.fetchall()
            notes = []
            for row in rows:
                notes.append(Note(
                    Note_ID=row[0],
                    Student_ID=row[1],
                    Original_File=row[2],
                    Summary_Text=row[3],
                    Upload_Date=row[4]
                ))
            return notes
        finally:
            conn.close()

    def create(self, note):
        """Create a new note"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Note (Student_ID, Original_File, Summary_Text, Upload_Date) OUTPUT INSERTED.Note_ID VALUES (?, ?, ?, ?)",
                (note.Student_ID, note.Original_File, note.Summary_Text, note.Upload_Date)
            )
            note_id = cursor.fetchone()[0]
            conn.commit()
            note.Note_ID = note_id
            return note
        finally:
            conn.close()

    def update(self, note):
        """Update an existing note"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Note SET Summary_Text = ? WHERE Note_ID = ?",
                (note.Summary_Text, note.Note_ID)
            )
            conn.commit()
            return note
        finally:
            conn.close()

    def delete(self, note_id):
        """Delete a note by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Note WHERE Note_ID = ?", (note_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()


    

