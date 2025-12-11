"""
User Settings Model
Represents user preferences and settings
"""
from datetime import datetime
from typing import Optional


class UserSettings:
    def __init__(
        self,
        Setting_ID: Optional[int] = None,
        User_ID: int = 0,
        email_notifications: bool = True,
        push_notifications: bool = True,
        calendar_reminders: bool = True,
        assignment_deadlines: bool = True,
        sync_google_calendar: bool = False,
        calendar_default_view: str = 'week',
        timezone: str = 'Africa/Cairo',
        theme: str = 'dark',
        language: str = 'en',
        colorblind_mode: bool = False,
        dyslexia_font: bool = False,
        profile_visibility: str = 'public',
        share_schedule: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs
    ):
        self.Setting_ID = Setting_ID
        self.User_ID = User_ID
        
        # Notification settings
        self.email_notifications = email_notifications
        self.push_notifications = push_notifications
        self.calendar_reminders = calendar_reminders
        self.assignment_deadlines = assignment_deadlines
        
        # Calendar settings
        self.sync_google_calendar = sync_google_calendar
        self.calendar_default_view = calendar_default_view
        self.timezone = timezone
        
        # Appearance settings
        self.theme = theme
        self.language = language
        self.colorblind_mode = colorblind_mode
        self.dyslexia_font = dyslexia_font
        
        # Privacy settings
        self.profile_visibility = profile_visibility
        self.share_schedule = share_schedule
        
        # Timestamps
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def __repr__(self):
        return f"<UserSettings(Setting_ID={self.Setting_ID}, User_ID={self.User_ID})>"

    def to_dict(self):
        """Convert settings to dictionary for JSON serialization"""
        return {
            'Setting_ID': self.Setting_ID,
            'User_ID': self.User_ID,
            'notifications': {
                'email': self.email_notifications,
                'push': self.push_notifications,
                'calendar_reminders': self.calendar_reminders,
                'assignment_deadlines': self.assignment_deadlines
            },
            'calendar': {
                'sync_google': self.sync_google_calendar,
                'default_view': self.calendar_default_view,
                'timezone': self.timezone
            },
            'appearance': {
                'theme': self.theme,
                'language': self.language,
                'colorblind_mode': self.colorblind_mode,
                'dyslexia_font': self.dyslexia_font
            },
            'privacy': {
                'profile_visibility': self.profile_visibility,
                'share_schedule': self.share_schedule
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def from_dict(data: dict) -> 'UserSettings':
        """Create UserSettings object from dictionary"""
        # Flatten nested dictionary structure
        flat_data = {
            'User_ID': data.get('User_ID'),
            'email_notifications': data.get('notifications', {}).get('email', True),
            'push_notifications': data.get('notifications', {}).get('push', True),
            'calendar_reminders': data.get('notifications', {}).get('calendar_reminders', True),
            'assignment_deadlines': data.get('notifications', {}).get('assignment_deadlines', True),
            'sync_google_calendar': data.get('calendar', {}).get('sync_google', False),
            'calendar_default_view': data.get('calendar', {}).get('default_view', 'week'),
            'timezone': data.get('calendar', {}).get('timezone', 'Africa/Cairo'),
            'theme': data.get('appearance', {}).get('theme', 'dark'),
            'language': data.get('appearance', {}).get('language', 'en'),
            'colorblind_mode': data.get('appearance', {}).get('colorblind_mode', False),
            'dyslexia_font': data.get('appearance', {}).get('dyslexia_font', False),
            'profile_visibility': data.get('privacy', {}).get('profile_visibility', 'public'),
            'share_schedule': data.get('privacy', {}).get('share_schedule', False)
        }
        return UserSettings(**flat_data)

