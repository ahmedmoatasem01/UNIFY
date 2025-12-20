"""
Course Model
Represents a course
"""
from typing import Optional


class Course:
    def __init__(self, Course_ID: Optional[int] = None, Course_Name: str = "",
                 Credits: int = 0, Instructor_ID: int = 0,
                 Schedule: Optional[str] = None, **kwargs):
        self.Course_ID = Course_ID
        self.Course_Name = Course_Name
        self.Credits = Credits
        self.Instructor_ID = Instructor_ID
        self.Schedule = Schedule
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<Course(Course_ID={self.Course_ID}, Course_Name='{self.Course_Name}', Credits={self.Credits})>"
    
    def to_dict(self):
        """Convert course to dictionary"""
        return {
            'Course_ID': self.Course_ID,
            'Course_Name': self.Course_Name,
            'Credits': self.Credits,
            'Instructor_ID': self.Instructor_ID,
            'Schedule': self.Schedule
        }

