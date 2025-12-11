"""
Task Model
Represents a task/assignment for a student
"""
from datetime import datetime
from typing import Optional


class Task:
    def __init__(self, Task_ID: Optional[int] = None, Student_ID: int = 0,
                 Task_Title: str = "", Due_Date: Optional[datetime] = None,
                 Priority: str = "medium", Status: str = "pending", **kwargs):
        self.Task_ID = Task_ID
        self.Student_ID = Student_ID
        self.Task_Title = Task_Title
        self.Due_Date = Due_Date
        self.Priority = Priority  # 'low', 'medium', 'high'
        self.Status = Status  # 'pending', 'completed'
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<Task(Task_ID={self.Task_ID}, Student_ID={self.Student_ID}, Task_Title='{self.Task_Title}', Status='{self.Status}')>"
    
    def to_dict(self):
        """Convert task to dictionary"""
        from datetime import datetime
        due_date_str = None
        if self.Due_Date:
            if isinstance(self.Due_Date, datetime):
                due_date_str = self.Due_Date.isoformat()
            elif isinstance(self.Due_Date, str):
                due_date_str = self.Due_Date
            else:
                # Handle SQL Server datetime objects
                try:
                    due_date_str = str(self.Due_Date)
                except:
                    due_date_str = None
        
        return {
            'Task_ID': self.Task_ID,
            'Student_ID': self.Student_ID,
            'Task_Title': self.Task_Title,
            'Due_Date': due_date_str,
            'Priority': self.Priority,
            'Status': self.Status
        }

