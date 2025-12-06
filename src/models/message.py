"""
Message Model
Represents a message between users
"""
from datetime import datetime
from typing import Optional


class Message:
    def __init__(self, Message_ID: Optional[int] = None, Sender_ID: int = 0,
                 Receiver_ID: int = 0, Message_Text: str = "",
                 Timestamp: Optional[datetime] = None, **kwargs):
        self.Message_ID = Message_ID
        self.Sender_ID = Sender_ID
        self.Receiver_ID = Receiver_ID
        self.Message_Text = Message_Text
        self.Timestamp = Timestamp or datetime.now()
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<Message(Message_ID={self.Message_ID}, Sender_ID={self.Sender_ID}, Receiver_ID={self.Receiver_ID})>"
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'Message_ID': self.Message_ID,
            'Sender_ID': self.Sender_ID,
            'Receiver_ID': self.Receiver_ID,
            'Message_Text': self.Message_Text,
            'Timestamp': self.Timestamp
        }

