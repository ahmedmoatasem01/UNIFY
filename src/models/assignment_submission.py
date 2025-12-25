"""
Assignment Submission Model
Represents a student's submission for an assignment
"""
from datetime import datetime
from typing import Optional


class AssignmentSubmission:
    """Assignment submission model"""
    
    def __init__(self,
                 Submission_ID: Optional[int] = None,
                 Assignment_ID: int = None,
                 Student_ID: int = None,
                 File_Path: Optional[str] = None,
                 File_Name: Optional[str] = None,
                 Submitted_At: Optional[datetime] = None,
                 Status: str = 'submitted',  # 'submitted', 'late', 'graded'
                 Grade: Optional[float] = None,
                 Feedback: Optional[str] = None,
                 Graded_By: Optional[int] = None,  # Instructor_ID or -1 for AI
                 Graded_At: Optional[datetime] = None,
                 Submission_Text: Optional[str] = None,
                 Review_Requested: bool = False,
                 Review_Comment: Optional[str] = None,
                 Is_AI_Graded: bool = False):
        self.Submission_ID = Submission_ID
        self.Assignment_ID = Assignment_ID
        self.Student_ID = Student_ID
        self.File_Path = File_Path
        self.File_Name = File_Name
        self.Submitted_At = Submitted_At or datetime.now()
        self.Status = Status
        self.Grade = Grade
        self.Feedback = Feedback
        self.Graded_By = Graded_By
        self.Graded_At = Graded_At
        self.Submission_Text = Submission_Text
        self.Review_Requested = Review_Requested
        self.Review_Comment = Review_Comment
        self.Is_AI_Graded = Is_AI_Graded
    
    def to_dict(self):
        """Convert submission to dictionary"""
        return {
            'submission_id': self.Submission_ID,
            'assignment_id': self.Assignment_ID,
            'student_id': self.Student_ID,
            'file_path': self.File_Path,
            'file_name': self.File_Name,
            'submitted_at': self.Submitted_At.isoformat() if self.Submitted_At else None,
            'status': self.Status,
            'grade': float(self.Grade) if self.Grade is not None else None,
            'feedback': self.Feedback,
            'graded_by': self.Graded_By,
            'graded_at': self.Graded_At.isoformat() if self.Graded_At else None,
            'submission_text': self.Submission_Text,
            'review_requested': bool(self.Review_Requested) if hasattr(self, 'Review_Requested') else False,
            'review_comment': self.Review_Comment if hasattr(self, 'Review_Comment') else None,
            'is_ai_graded': bool(self.Is_AI_Graded) if hasattr(self, 'Is_AI_Graded') else False
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create submission from dictionary"""
        submitted_at = None
        if data.get('Submitted_At'):
            if isinstance(data['Submitted_At'], str):
                submitted_at = datetime.fromisoformat(data['Submitted_At'].replace('Z', '+00:00'))
            else:
                submitted_at = data['Submitted_At']
        
        graded_at = None
        if data.get('Graded_At'):
            if isinstance(data['Graded_At'], str):
                graded_at = datetime.fromisoformat(data['Graded_At'].replace('Z', '+00:00'))
            else:
                graded_at = data['Graded_At']
        
        return cls(
            Submission_ID=data.get('Submission_ID'),
            Assignment_ID=data.get('Assignment_ID'),
            Student_ID=data.get('Student_ID'),
            File_Path=data.get('File_Path'),
            File_Name=data.get('File_Name'),
            Submitted_At=submitted_at,
            Status=data.get('Status', 'submitted'),
            Grade=data.get('Grade'),
            Feedback=data.get('Feedback'),
            Graded_By=data.get('Graded_By'),
            Graded_At=graded_at,
            Submission_Text=data.get('Submission_Text'),
            Review_Requested=data.get('Review_Requested', False),
            Review_Comment=data.get('Review_Comment'),
            Is_AI_Graded=data.get('Is_AI_Graded', False)
        )
