"""
Calendar Model
Represents a calendar event for a student
"""
from datetime import date, time
from typing import Optional


class Calendar:
    def __init__(self, Event_ID: Optional[int] = None, Student_ID: int = 0,
                 Title: str = "", Date: Optional[date] = None,
                 Time: Optional[time] = None, Source: Optional[str] = None, **kwargs):
        self.Event_ID = Event_ID
        self.Student_ID = Student_ID
        self.Title = Title
        self.Date = Date
        self.Time = Time
        self.Source = Source
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<Calendar(Event_ID={self.Event_ID}, Student_ID={self.Student_ID}, Title='{self.Title}')>"
    
    def to_dict(self):
        """Convert calendar event to dictionary"""
        return {
            'Event_ID': self.Event_ID,
            'Student_ID': self.Student_ID,
            'Title': self.Title,
            'Date': self.Date,
            'Time': self.Time,
            'Source': self.Source
        }

