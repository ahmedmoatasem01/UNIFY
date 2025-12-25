"""
Deadline Notification Preference Model
Represents user preferences for deadline notifications
"""
from typing import Optional
import json


class DeadlineNotificationPreference:
    def __init__(
        self,
        Preference_ID: Optional[int] = None,
        User_ID: int = 0,
        Deadline_Type: str = "all",  # 'task', 'assignment', 'exam', 'all'
        Alert_Intervals: Optional[str] = None,  # JSON array string: "[4320, 1440, 60]"
        Email_Enabled: bool = False,
        In_App_Enabled: bool = True,
        Quiet_Hours_Start: Optional[str] = None,  # TIME format: "HH:MM:SS"
        Quiet_Hours_End: Optional[str] = None,  # TIME format: "HH:MM:SS"
        **kwargs
    ):
        self.Preference_ID = Preference_ID
        self.User_ID = User_ID
        self.Deadline_Type = Deadline_Type
        self.Alert_Intervals = Alert_Intervals or "[4320, 1440, 60]"  # Default: 3 days, 1 day, 1 hour
        self.Email_Enabled = Email_Enabled
        self.In_App_Enabled = In_App_Enabled
        self.Quiet_Hours_Start = Quiet_Hours_Start
        self.Quiet_Hours_End = Quiet_Hours_End
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<DeadlineNotificationPreference(Preference_ID={self.Preference_ID}, User_ID={self.User_ID}, Deadline_Type='{self.Deadline_Type}')>"
    
    def get_alert_intervals_list(self):
        """Parse Alert_Intervals JSON string and return as list"""
        try:
            if isinstance(self.Alert_Intervals, str):
                return json.loads(self.Alert_Intervals)
            elif isinstance(self.Alert_Intervals, list):
                return self.Alert_Intervals
            else:
                return [4320, 1440, 60]  # Default intervals
        except:
            return [4320, 1440, 60]  # Default intervals
    
    def set_alert_intervals_list(self, intervals: list):
        """Set Alert_Intervals from a list"""
        try:
            self.Alert_Intervals = json.dumps(intervals)
        except:
            self.Alert_Intervals = "[4320, 1440, 60]"
    
    def to_dict(self):
        """Convert preference to dictionary"""
        return {
            'Preference_ID': self.Preference_ID,
            'User_ID': self.User_ID,
            'Deadline_Type': self.Deadline_Type,
            'Alert_Intervals': self.Alert_Intervals,
            'Alert_Intervals_List': self.get_alert_intervals_list(),
            'Email_Enabled': self.Email_Enabled,
            'In_App_Enabled': self.In_App_Enabled,
            'Quiet_Hours_Start': self.Quiet_Hours_Start,
            'Quiet_Hours_End': self.Quiet_Hours_End
        }

