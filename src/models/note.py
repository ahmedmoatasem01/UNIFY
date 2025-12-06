"""
Note Model
Represents a note/lecture summary for a student
"""
from datetime import datetime
from typing import Optional


class Note:
    def __init__(self, Note_ID: Optional[int] = None, Student_ID: int = 0,
                 Original_File: str = "", Summary_Text: Optional[str] = None,
                 Upload_Date: Optional[datetime] = None, **kwargs):
        self.Note_ID = Note_ID
        self.Student_ID = Student_ID
        self.Original_File = Original_File
        self.Summary_Text = Summary_Text
        self.Upload_Date = Upload_Date or datetime.now()
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<Note(Note_ID={self.Note_ID}, Student_ID={self.Student_ID}, Original_File='{self.Original_File}')>"
    
    def to_dict(self):
        """Convert note to dictionary"""
        return {
            'Note_ID': self.Note_ID,
            'Student_ID': self.Student_ID,
            'Original_File': self.Original_File,
            'Summary_Text': self.Summary_Text,
            'Upload_Date': self.Upload_Date
        }

