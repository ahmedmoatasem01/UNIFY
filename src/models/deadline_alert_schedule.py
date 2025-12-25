"""
Deadline Alert Schedule Model
Represents a scheduled alert for a deadline notification
"""
from datetime import datetime
from typing import Optional


class DeadlineAlertSchedule:
    def __init__(
        self,
        Schedule_ID: Optional[int] = None,
        Notification_ID: int = 0,
        Alert_Time_Before_Deadline: int = 0,  # Minutes before deadline
        Alert_Type: str = "in_app",  # 'in_app', 'email', 'push'
        Is_Sent: bool = False,
        Sent_At: Optional[datetime] = None,
        **kwargs
    ):
        self.Schedule_ID = Schedule_ID
        self.Notification_ID = Notification_ID
        self.Alert_Time_Before_Deadline = Alert_Time_Before_Deadline
        self.Alert_Type = Alert_Type
        self.Is_Sent = Is_Sent
        self.Sent_At = Sent_At
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<DeadlineAlertSchedule(Schedule_ID={self.Schedule_ID}, Notification_ID={self.Notification_ID}, Alert_Time_Before_Deadline={self.Alert_Time_Before_Deadline})>"
    
    def to_dict(self):
        """Convert alert schedule to dictionary"""
        sent_at_str = None
        if self.Sent_At:
            if isinstance(self.Sent_At, datetime):
                sent_at_str = self.Sent_At.isoformat()
            elif isinstance(self.Sent_At, str):
                sent_at_str = self.Sent_At
            else:
                try:
                    sent_at_str = str(self.Sent_At)
                except:
                    sent_at_str = None
        
        return {
            'Schedule_ID': self.Schedule_ID,
            'Notification_ID': self.Notification_ID,
            'Alert_Time_Before_Deadline': self.Alert_Time_Before_Deadline,
            'Alert_Type': self.Alert_Type,
            'Is_Sent': self.Is_Sent,
            'Sent_At': sent_at_str
        }

