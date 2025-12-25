"""
Study Task Model
Represents a task within a study plan (can be a subtask with parent)
"""
from typing import Optional
from datetime import datetime


class StudyTask:
    def __init__(self, Task_ID: Optional[int] = None, Plan_ID: int = 0,
                 Parent_Task_ID: Optional[int] = None, Task_Title: str = '',
                 Description: Optional[str] = None, Estimated_Hours: Optional[float] = None,
                 Actual_Hours: Optional[float] = None, Due_Date: Optional[datetime] = None,
                 Priority: str = 'medium', Status: str = 'pending',
                 Suggested_Resources: Optional[str] = None, Created_At: Optional[datetime] = None, **kwargs):
        self.Task_ID = Task_ID
        self.Plan_ID = Plan_ID
        self.Parent_Task_ID = Parent_Task_ID
        self.Task_Title = Task_Title
        self.Description = Description
        self.Estimated_Hours = Estimated_Hours
        self.Actual_Hours = Actual_Hours
        self.Due_Date = Due_Date
        self.Priority = Priority  # 'low', 'medium', 'high'
        self.Status = Status  # 'pending', 'in_progress', 'completed', 'skipped'
        self.Suggested_Resources = Suggested_Resources  # JSON string
        self.Created_At = Created_At or datetime.now()
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<StudyTask(Task_ID={self.Task_ID}, Plan_ID={self.Plan_ID}, Task_Title='{self.Task_Title}', Status='{self.Status}')>"
    
    def to_dict(self):
        """Convert study task to dictionary"""
        return {
            'Task_ID': self.Task_ID,
            'Plan_ID': self.Plan_ID,
            'Parent_Task_ID': self.Parent_Task_ID,
            'Task_Title': self.Task_Title,
            'Description': self.Description,
            'Estimated_Hours': float(self.Estimated_Hours) if self.Estimated_Hours else None,
            'Actual_Hours': float(self.Actual_Hours) if self.Actual_Hours else None,
            'Due_Date': self.Due_Date.isoformat() if self.Due_Date else None,
            'Priority': self.Priority,
            'Status': self.Status,
            'Suggested_Resources': self.Suggested_Resources,
            'Created_At': self.Created_At.isoformat() if self.Created_At else None
        }

