"""
Notification Model
Represents a notification for a user
"""
from datetime import datetime
from typing import Optional


class Notification:
    """Notification model"""
    
    def __init__(self, 
                 Notification_ID: Optional[int] = None,
                 User_ID: int = None,
                 Title: str = None,
                 Message: str = None,
                 Type: str = None,
                 Priority: str = 'medium',
                 Is_Read: bool = False,
                 Action_URL: Optional[str] = None,
                 Created_At: Optional[datetime] = None,
                 Read_At: Optional[datetime] = None):
        self.Notification_ID = Notification_ID
        self.User_ID = User_ID
        self.Title = Title
        self.Message = Message
        self.Type = Type  # 'task', 'assignment', 'grade', 'announcement', 'system', 'message'
        self.Priority = Priority  # 'low', 'medium', 'high', 'urgent'
        self.Is_Read = Is_Read
        self.Action_URL = Action_URL
        self.Created_At = Created_At or datetime.now()
        self.Read_At = Read_At
    
    def to_dict(self):
        """Convert notification to dictionary"""
        return {
            'notification_id': self.Notification_ID,
            'user_id': self.User_ID,
            'title': self.Title,
            'message': self.Message,
            'type': self.Type,
            'priority': self.Priority,
            'is_read': bool(self.Is_Read),
            'action_url': self.Action_URL,
            'created_at': self.Created_At.isoformat() if self.Created_At else None,
            'read_at': self.Read_At.isoformat() if self.Read_At else None
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create notification from dictionary"""
        created_at = None
        if data.get('Created_At'):
            if isinstance(data['Created_At'], str):
                created_at = datetime.fromisoformat(data['Created_At'].replace('Z', '+00:00'))
            else:
                created_at = data['Created_At']
        
        read_at = None
        if data.get('Read_At'):
            if isinstance(data['Read_At'], str):
                read_at = datetime.fromisoformat(data['Read_At'].replace('Z', '+00:00'))
            else:
                read_at = data['Read_At']
        
        return cls(
            Notification_ID=data.get('Notification_ID'),
            User_ID=data.get('User_ID'),
            Title=data.get('Title'),
            Message=data.get('Message'),
            Type=data.get('Type'),
            Priority=data.get('Priority', 'medium'),
            Is_Read=data.get('Is_Read', False),
            Action_URL=data.get('Action_URL'),
            Created_At=created_at,
            Read_At=read_at
        )
