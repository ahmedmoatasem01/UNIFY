"""
Student Model
Represents a student user
"""
from typing import Optional


class Student:
    def __init__(self, Student_ID: Optional[int] = None, User_ID: int = 0,
                 Department: Optional[str] = None, Year_Level: Optional[int] = None,
                 GPA: Optional[float] = None, **kwargs):
        self.Student_ID = Student_ID
        self.User_ID = User_ID
        self.Department = Department
        self.Year_Level = Year_Level
        self.GPA = GPA
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<Student(Student_ID={self.Student_ID}, User_ID={self.User_ID}, Department='{self.Department}')>"
    
    def to_dict(self):
        """Convert student to dictionary"""
        return {
            'Student_ID': self.Student_ID,
            'User_ID': self.User_ID,
            'Department': self.Department,
            'Year_Level': self.Year_Level,
            'GPA': self.GPA
        }

