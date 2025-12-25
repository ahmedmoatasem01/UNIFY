"""
Study Plan Model
Represents an AI-generated personalized study plan for a student
"""
from typing import Optional
from datetime import datetime, date


class StudyPlan:
    def __init__(self, Plan_ID: Optional[int] = None, Student_ID: int = 0,
                 Course_ID: Optional[int] = None, Plan_Name: str = '',
                 Start_Date: Optional[date] = None, End_Date: Optional[date] = None,
                 Status: str = 'active', Completion_Percentage: float = 0.0,
                 Created_At: Optional[datetime] = None, **kwargs):
        self.Plan_ID = Plan_ID
        self.Student_ID = Student_ID
        self.Course_ID = Course_ID
        self.Plan_Name = Plan_Name
        self.Start_Date = Start_Date
        self.End_Date = End_Date
        self.Status = Status  # 'active', 'paused', 'completed', 'archived'
        self.Completion_Percentage = Completion_Percentage
        self.Created_At = Created_At or datetime.now()
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<StudyPlan(Plan_ID={self.Plan_ID}, Student_ID={self.Student_ID}, Plan_Name='{self.Plan_Name}', Status='{self.Status}')>"
    
    def to_dict(self):
        """Convert study plan to dictionary"""
        return {
            'Plan_ID': self.Plan_ID,
            'Student_ID': self.Student_ID,
            'Course_ID': self.Course_ID,
            'Plan_Name': self.Plan_Name,
            'Start_Date': self.Start_Date.isoformat() if self.Start_Date else None,
            'End_Date': self.End_Date.isoformat() if self.End_Date else None,
            'Status': self.Status,
            'Completion_Percentage': float(self.Completion_Percentage) if self.Completion_Percentage else 0.0,
            'Created_At': self.Created_At.isoformat() if self.Created_At else None
        }

