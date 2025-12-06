"""
Enrollment Model
Represents a student's enrollment in a course
"""
from typing import Optional


class Enrollment:
    def __init__(self, Enrollment_ID: Optional[int] = None, Student_ID: int = 0,
                 Course_ID: int = 0, Status: str = "enrolled", **kwargs):
        self.Enrollment_ID = Enrollment_ID
        self.Student_ID = Student_ID
        self.Course_ID = Course_ID
        self.Status = Status  # 'enrolled', 'dropped', 'completed'
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<Enrollment(Enrollment_ID={self.Enrollment_ID}, Student_ID={self.Student_ID}, Course_ID={self.Course_ID}, Status='{self.Status}')>"
    
    def to_dict(self):
        """Convert enrollment to dictionary"""
        return {
            'Enrollment_ID': self.Enrollment_ID,
            'Student_ID': self.Student_ID,
            'Course_ID': self.Course_ID,
            'Status': self.Status
        }

