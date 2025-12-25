"""
Study Recommendation Model
Represents AI-generated resource recommendations for students
"""
from datetime import datetime
from typing import Optional


class StudyRecommendation:
    def __init__(self, Recommendation_ID: Optional[int] = None, Student_ID: int = 0,
                 Course_ID: Optional[int] = None, Topic: Optional[str] = None,
                 Resource_Type: Optional[str] = None, Resource_Link: Optional[str] = None,
                 Reason: Optional[str] = None, Relevance_Score: Optional[float] = None,
                 Generated_At: Optional[datetime] = None, **kwargs):
        self.Recommendation_ID = Recommendation_ID
        self.Student_ID = Student_ID
        self.Course_ID = Course_ID
        self.Topic = Topic
        self.Resource_Type = Resource_Type  # 'note', 'video', 'practice', 'textbook'
        self.Resource_Link = Resource_Link
        self.Reason = Reason
        self.Relevance_Score = Relevance_Score
        self.Generated_At = Generated_At or datetime.now()
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<StudyRecommendation(Recommendation_ID={self.Recommendation_ID}, Topic='{self.Topic}', Resource_Type='{self.Resource_Type}')>"
    
    def to_dict(self):
        """Convert study recommendation to dictionary"""
        return {
            'Recommendation_ID': self.Recommendation_ID,
            'Student_ID': self.Student_ID,
            'Course_ID': self.Course_ID,
            'Topic': self.Topic,
            'Resource_Type': self.Resource_Type,
            'Resource_Link': self.Resource_Link,
            'Reason': self.Reason,
            'Relevance_Score': float(self.Relevance_Score) if self.Relevance_Score else None,
            'Generated_At': self.Generated_At.isoformat() if isinstance(self.Generated_At, datetime) else str(self.Generated_At) if self.Generated_At else None
        }
