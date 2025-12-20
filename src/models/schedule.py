"""
Schedule Model
Represents a student's schedule
"""
from typing import Optional


class Schedule:
    def __init__(self, Schedule_ID: Optional[int] = None, Student_ID: int = 0,
                 Course_List: Optional[str] = None, Optimized: bool = False, **kwargs):
        self.Schedule_ID = Schedule_ID
        self.Student_ID = Student_ID
        self.Course_List = Course_List
        self.Optimized = bool(Optimized) if Optimized is not None else False
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<Schedule(Schedule_ID={self.Schedule_ID}, Student_ID={self.Student_ID}, Optimized={self.Optimized})>"
    
    def to_dict(self):
        """Convert schedule to dictionary"""
        return {
            'Schedule_ID': self.Schedule_ID,
            'Student_ID': self.Student_ID,
            'Course_List': self.Course_List,
            'Optimized': self.Optimized
        }

