"""
Advisor Appointment Model
Represents an appointment scheduled between a student and advisor
"""
from typing import Optional
from datetime import datetime


class AdvisorAppointment:
    def __init__(self, Appointment_ID: Optional[int] = None, Student_ID: int = 0,
                 Advisor_ID: int = 0, Scheduled_Date: Optional[datetime] = None,
                 Reason: Optional[str] = None, Status: Optional[str] = 'pending',
                 Created_From_Conversation_ID: Optional[int] = None,
                 Instructor_Response: Optional[str] = None, **kwargs):
        self.Appointment_ID = Appointment_ID
        self.Student_ID = Student_ID
        self.Advisor_ID = Advisor_ID
        self.Scheduled_Date = Scheduled_Date
        self.Reason = Reason
        self.Status = Status  # 'pending', 'scheduled', 'completed', 'cancelled', 'rejected'
        self.Created_From_Conversation_ID = Created_From_Conversation_ID
        self.Instructor_Response = Instructor_Response
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<AdvisorAppointment(Appointment_ID={self.Appointment_ID}, Student_ID={self.Student_ID}, Advisor_ID={self.Advisor_ID}, Status='{self.Status}')>"
    
    def to_dict(self):
        """Convert appointment to dictionary"""
        return {
            'Appointment_ID': self.Appointment_ID,
            'Student_ID': self.Student_ID,
            'Advisor_ID': self.Advisor_ID,
            'Scheduled_Date': self.Scheduled_Date.isoformat() if self.Scheduled_Date else None,
            'Reason': self.Reason,
            'Status': self.Status,
            'Created_From_Conversation_ID': self.Created_From_Conversation_ID,
            'Instructor_Response': self.Instructor_Response
        }
