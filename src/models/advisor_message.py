"""
Advisor Message Model
Represents a message within an advisor conversation
"""
from typing import Optional
from datetime import datetime


class AdvisorMessage:
    def __init__(self, Message_ID: Optional[int] = None, Conversation_ID: int = 0,
                 Sender_Type: Optional[str] = None, Message_Text: str = '',
                 Intent: Optional[str] = None, Confidence_Score: Optional[float] = None,
                 Sent_At: Optional[datetime] = None, **kwargs):
        self.Message_ID = Message_ID
        self.Conversation_ID = Conversation_ID
        self.Sender_Type = Sender_Type  # 'student', 'ai', 'advisor'
        self.Message_Text = Message_Text
        self.Intent = Intent  # Detected intent (e.g., 'course_recommendation', 'prerequisite_check')
        self.Confidence_Score = Confidence_Score
        self.Sent_At = Sent_At
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<AdvisorMessage(Message_ID={self.Message_ID}, Conversation_ID={self.Conversation_ID}, Sender='{self.Sender_Type}', Intent='{self.Intent}')>"
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'Message_ID': self.Message_ID,
            'Conversation_ID': self.Conversation_ID,
            'Sender_Type': self.Sender_Type,
            'Message_Text': self.Message_Text,
            'Intent': self.Intent,
            'Confidence_Score': float(self.Confidence_Score) if self.Confidence_Score is not None else None,
            'Sent_At': self.Sent_At.isoformat() if self.Sent_At else None
        }
