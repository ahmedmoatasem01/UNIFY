"""
Teaching Assistant Model
Represents a teaching assistant
"""
from typing import Optional


class TeachingAssistant:
    def __init__(self, TA_ID: Optional[int] = None, User_ID: int = 0,
                 Assigned_Course_ID: int = 0, Role: str = "Teaching Assistant",
                 Hours_Per_Week: Optional[int] = None, **kwargs):
        self.TA_ID = TA_ID
        self.User_ID = User_ID
        self.Assigned_Course_ID = Assigned_Course_ID
        self.Role = Role
        self.Hours_Per_Week = Hours_Per_Week
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<TeachingAssistant(TA_ID={self.TA_ID}, User_ID={self.User_ID}, Assigned_Course_ID={self.Assigned_Course_ID}, Role='{self.Role}')>"
    
    def to_dict(self):
        """Convert teaching assistant to dictionary"""
        return {
            'TA_ID': self.TA_ID,
            'User_ID': self.User_ID,
            'Assigned_Course_ID': self.Assigned_Course_ID,
            'Role': self.Role,
            'Hours_Per_Week': self.Hours_Per_Week
        }

