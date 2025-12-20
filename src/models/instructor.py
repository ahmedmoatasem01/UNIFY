"""
Instructor Model
Represents an instructor user
"""
from typing import Optional


class Instructor:
    def __init__(self, Instructor_ID: Optional[int] = None, User_ID: int = 0,
                 Department: Optional[str] = None, Office: Optional[str] = None,
                 Email: Optional[str] = None, **kwargs):
        self.Instructor_ID = Instructor_ID
        self.User_ID = User_ID
        self.Department = Department
        self.Office = Office
        self.Email = Email
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<Instructor(Instructor_ID={self.Instructor_ID}, User_ID={self.User_ID}, Department='{self.Department}')>"
    
    def to_dict(self):
        """Convert instructor to dictionary"""
        return {
            'Instructor_ID': self.Instructor_ID,
            'User_ID': self.User_ID,
            'Department': self.Department,
            'Office': self.Office,
            'Email': self.Email
        }

