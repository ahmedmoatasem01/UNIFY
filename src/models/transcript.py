"""
Transcript Model
Represents a student's transcript
"""
from datetime import datetime
from typing import Optional


class Transcript:
    def __init__(self, Transcript_ID: Optional[int] = None, Student_ID: int = 0,
                 GPA: Optional[float] = None, PDF_Path: str = "",
                 Issue_Date: Optional[datetime] = None, **kwargs):
        self.Transcript_ID = Transcript_ID
        self.Student_ID = Student_ID
        self.GPA = GPA
        self.PDF_Path = PDF_Path
        self.Issue_Date = Issue_Date or datetime.now()
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<Transcript(Transcript_ID={self.Transcript_ID}, Student_ID={self.Student_ID}, GPA={self.GPA})>"
    
    def to_dict(self):
        """Convert transcript to dictionary"""
        return {
            'Transcript_ID': self.Transcript_ID,
            'Student_ID': self.Student_ID,
            'GPA': self.GPA,
            'PDF_Path': self.PDF_Path,
            'Issue_Date': self.Issue_Date
        }

