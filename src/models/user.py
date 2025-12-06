"""
User Model
Represents a user in the system
"""
from datetime import datetime
from typing import Optional


class User:
    def __init__(self, User_ID: Optional[int] = None, Username: str = "", 
                 Email: str = "", Password_Hash: str = "", 
                 Created_At: Optional[datetime] = None, **kwargs):
        self.User_ID = User_ID
        self.Username = Username
        self.Email = Email
        self.Password_Hash = Password_Hash
        self.Created_At = Created_At or datetime.now()
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<User(User_ID={self.User_ID}, Username='{self.Username}', Email='{self.Email}')>"
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'User_ID': self.User_ID,
            'Username': self.Username,
            'Email': self.Email,
            'Password_Hash': self.Password_Hash,
            'Created_At': self.Created_At
        }

