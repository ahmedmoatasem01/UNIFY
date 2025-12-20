"""
Message Model
Represents a message between users
"""
from datetime import datetime
from typing import Optional


class Message:
    def __init__(self, Message_ID: Optional[int] = None, Sender_ID: int = 0,
                 Receiver_ID: int = 0, Message_Text: str = "",
                 Timestamp: Optional[datetime] = None, Is_Read: bool = False, **kwargs):
        self.Message_ID = Message_ID
        self.Sender_ID = Sender_ID
        self.Receiver_ID = Receiver_ID
        self.Message_Text = Message_Text
        self.Timestamp = Timestamp or datetime.now()
        self.Is_Read = Is_Read
        
        # Additional fields for display purposes
        self.Sender_Name = kwargs.get('Sender_Name', None)
        self.Receiver_Name = kwargs.get('Receiver_Name', None)
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        return f"<Message(Message_ID={self.Message_ID}, Sender_ID={self.Sender_ID}, Receiver_ID={self.Receiver_ID})>"
    
    def to_dict(self, current_user_id=None):
        """Convert message to dictionary"""
        result = {
            'Message_ID': self.Message_ID,
            'Sender_ID': self.Sender_ID,
            'Receiver_ID': self.Receiver_ID,
            'Message_Text': self.Message_Text,
            'Timestamp': self.Timestamp.isoformat() if self.Timestamp else None,
            'Is_Read': self.Is_Read
        }
        
        # Add Is_Sent if current_user_id is provided
        if current_user_id is not None:
            result['Is_Sent'] = self.Sender_ID == current_user_id
        
        # Add optional display fields if present
        if hasattr(self, 'Sender_Name') and self.Sender_Name:
            result['Sender_Name'] = self.Sender_Name
        if hasattr(self, 'Receiver_Name') and self.Receiver_Name:
            result['Receiver_Name'] = self.Receiver_Name
            
        return result

