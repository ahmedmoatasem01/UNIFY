"""
Grading Suggestion Model
Represents AI-generated grading suggestions
"""
from datetime import datetime
from typing import Optional


class GradingSuggestion:
    """Grading suggestion model"""
    
    def __init__(self,
                 Suggestion_ID: Optional[int] = None,
                 Submission_ID: int = None,
                 Suggested_Grade: Optional[float] = None,
                 Confidence_Score: Optional[float] = None,
                 Rubric_Scores: Optional[str] = None,  # JSON string
                 Feedback_Suggestions: Optional[str] = None,
                 Flagged_For_Review: bool = False,
                 Flag_Reason: Optional[str] = None,
                 Generated_At: Optional[datetime] = None,
                 Accepted: Optional[bool] = None):
        self.Suggestion_ID = Suggestion_ID
        self.Submission_ID = Submission_ID
        self.Suggested_Grade = Suggested_Grade
        self.Confidence_Score = Confidence_Score
        self.Rubric_Scores = Rubric_Scores
        self.Feedback_Suggestions = Feedback_Suggestions
        self.Flagged_For_Review = Flagged_For_Review
        self.Flag_Reason = Flag_Reason
        self.Generated_At = Generated_At or datetime.now()
        self.Accepted = Accepted
    
    def to_dict(self):
        """Convert suggestion to dictionary"""
        return {
            'suggestion_id': self.Suggestion_ID,
            'submission_id': self.Submission_ID,
            'suggested_grade': float(self.Suggested_Grade) if self.Suggested_Grade else None,
            'confidence_score': float(self.Confidence_Score) if self.Confidence_Score else None,
            'rubric_scores': self.Rubric_Scores,
            'feedback_suggestions': self.Feedback_Suggestions,
            'flagged_for_review': bool(self.Flagged_For_Review),
            'flag_reason': self.Flag_Reason,
            'generated_at': self.Generated_At.isoformat() if self.Generated_At else None,
            'accepted': bool(self.Accepted) if self.Accepted is not None else None
        }
