"""
Focus Session Model
Represents a Pomodoro/focus session for a student
"""
from datetime import datetime
from typing import Optional


class FocusSession:
    def __init__(self, Session_ID: Optional[int] = None, Student_ID: int = 0,
                 Duration: int = 0, Start_Time: Optional[datetime] = None,
                 End_Time: Optional[datetime] = None, Completed: bool = False, **kwargs):
        self.Session_ID = Session_ID
        self.Student_ID = Student_ID
        self.Duration = Duration
        self.Start_Time = Start_Time
        self.End_Time = End_Time
        self.Completed = bool(Completed) if Completed is not None else False
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<FocusSession(Session_ID={self.Session_ID}, Student_ID={self.Student_ID}, Duration={self.Duration}, Completed={self.Completed})>"
    
    def to_dict(self):
        """Convert focus session to dictionary"""
        return {
            'Session_ID': self.Session_ID,
            'Student_ID': self.Student_ID,
            'Duration': self.Duration,
            'Start_Time': self.Start_Time,
            'End_Time': self.End_Time,
            'Completed': self.Completed
        }

