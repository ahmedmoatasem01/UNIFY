"""
Notification Preference Model
Represents user preferences for notification types
"""
from typing import Optional


class NotificationPreference:
    """Notification preference model"""
    
    def __init__(self,
                 Preference_ID: Optional[int] = None,
                 User_ID: int = None,
                 Notification_Type: str = None,
                 Email_Enabled: bool = False,
                 In_App_Enabled: bool = True):
        self.Preference_ID = Preference_ID
        self.User_ID = User_ID
        self.Notification_Type = Notification_Type
        self.Email_Enabled = Email_Enabled
        self.In_App_Enabled = In_App_Enabled
    
    def to_dict(self):
        """Convert preference to dictionary"""
        return {
            'preference_id': self.Preference_ID,
            'user_id': self.User_ID,
            'notification_type': self.Notification_Type,
            'email_enabled': bool(self.Email_Enabled),
            'in_app_enabled': bool(self.In_App_Enabled)
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create preference from dictionary"""
        return cls(
            Preference_ID=data.get('Preference_ID'),
            User_ID=data.get('User_ID'),
            Notification_Type=data.get('Notification_Type'),
            Email_Enabled=data.get('Email_Enabled', False),
            In_App_Enabled=data.get('In_App_Enabled', True)
        )
