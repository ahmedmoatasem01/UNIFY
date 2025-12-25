"""
Advisor Conversation Model
Represents a conversation between a student and the AI academic advisor
"""
from typing import Optional
from datetime import datetime


class AdvisorConversation:
    def __init__(self, Conversation_ID: Optional[int] = None, Student_ID: int = 0,
                 Conversation_Type: Optional[str] = None, Started_At: Optional[datetime] = None,
                 Last_Message_At: Optional[datetime] = None, Status: Optional[str] = 'active',
                 Escalated_To_Advisor_ID: Optional[int] = None, **kwargs):
        self.Conversation_ID = Conversation_ID
        self.Student_ID = Student_ID
        self.Conversation_Type = Conversation_Type  # 'degree_planning', 'course_selection', 'policy', 'career'
        self.Started_At = Started_At
        self.Last_Message_At = Last_Message_At
        self.Status = Status  # 'active', 'resolved', 'escalated', 'archived'
        self.Escalated_To_Advisor_ID = Escalated_To_Advisor_ID
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<AdvisorConversation(Conversation_ID={self.Conversation_ID}, Student_ID={self.Student_ID}, Type='{self.Conversation_Type}', Status='{self.Status}')>"
    
    def to_dict(self):
        """Convert conversation to dictionary"""
        return {
            'Conversation_ID': self.Conversation_ID,
            'Student_ID': self.Student_ID,
            'Conversation_Type': self.Conversation_Type,
            'Started_At': self.Started_At.isoformat() if self.Started_At else None,
            'Last_Message_At': self.Last_Message_At.isoformat() if self.Last_Message_At else None,
            'Status': self.Status,
            'Escalated_To_Advisor_ID': self.Escalated_To_Advisor_ID
        }
