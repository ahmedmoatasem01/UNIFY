"""
Deadline Notification Model
Represents a deadline notification for a user
"""
from datetime import datetime
from typing import Optional


class DeadlineNotification:
    def __init__(
        self,
        Notification_ID: Optional[int] = None,
        User_ID: int = 0,
        Deadline_Type: str = "",
        Source_ID: int = 0,
        Source_Type: str = "",
        Deadline_Date: Optional[datetime] = None,
        Title: str = "",
        Description: Optional[str] = None,
        Priority: str = "medium",
        Status: str = "active",
        Created_At: Optional[datetime] = None,
        **kwargs
    ):
        self.Notification_ID = Notification_ID
        self.User_ID = User_ID
        self.Deadline_Type = Deadline_Type  # 'task', 'assignment', 'exam', 'project', 'calendar'
        self.Source_ID = Source_ID  # ID of the task, assignment, or event
        self.Source_Type = Source_Type  # 'task', 'assignment', 'calendar_event'
        self.Deadline_Date = Deadline_Date
        self.Title = Title
        self.Description = Description
        self.Priority = Priority  # 'low', 'medium', 'high', 'urgent'
        self.Status = Status  # 'active', 'completed', 'overdue', 'cancelled'
        self.Created_At = Created_At or datetime.now()
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<DeadlineNotification(Notification_ID={self.Notification_ID}, User_ID={self.User_ID}, Title='{self.Title}', Status='{self.Status}')>"
    
    def to_dict(self):
        """Convert deadline notification to dictionary"""
        deadline_date_str = None
        if self.Deadline_Date:
            if isinstance(self.Deadline_Date, datetime):
                deadline_date_str = self.Deadline_Date.isoformat()
            elif isinstance(self.Deadline_Date, str):
                deadline_date_str = self.Deadline_Date
            else:
                try:
                    deadline_date_str = str(self.Deadline_Date)
                except:
                    deadline_date_str = None
        
        created_at_str = None
        if self.Created_At:
            if isinstance(self.Created_At, datetime):
                created_at_str = self.Created_At.isoformat()
            elif isinstance(self.Created_At, str):
                created_at_str = self.Created_At
            else:
                try:
                    created_at_str = str(self.Created_At)
                except:
                    created_at_str = None
        
        return {
            'Notification_ID': self.Notification_ID,
            'User_ID': self.User_ID,
            'Deadline_Type': self.Deadline_Type,
            'Source_ID': self.Source_ID,
            'Source_Type': self.Source_Type,
            'Deadline_Date': deadline_date_str,
            'Title': self.Title,
            'Description': self.Description,
            'Priority': self.Priority,
            'Status': self.Status,
            'Created_At': created_at_str
        }

