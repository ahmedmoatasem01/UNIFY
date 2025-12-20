"""
Reminder Model
Represents a reminder for a calendar event
"""
from datetime import datetime
from typing import Optional


class Reminder:
    def __init__(self, Reminder_ID: Optional[int] = None, Student_ID: int = 0,
                 Event_ID: int = 0, Reminder_Time: Optional[datetime] = None,
                 Status: str = "pending", **kwargs):
        self.Reminder_ID = Reminder_ID
        self.Student_ID = Student_ID
        self.Event_ID = Event_ID
        self.Reminder_Time = Reminder_Time
        self.Status = Status  # 'pending', 'done'
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<Reminder(Reminder_ID={self.Reminder_ID}, Student_ID={self.Student_ID}, Event_ID={self.Event_ID}, Status='{self.Status}')>"
    
    def to_dict(self):
        """Convert reminder to dictionary"""
        return {
            'Reminder_ID': self.Reminder_ID,
            'Student_ID': self.Student_ID,
            'Event_ID': self.Event_ID,
            'Reminder_Time': self.Reminder_Time,
            'Status': self.Status
        }

