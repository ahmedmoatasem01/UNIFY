"""
Assignment Model
Represents an assignment created by instructors/TAs
"""
from datetime import datetime
from typing import Optional


class Assignment:
    """Assignment model"""
    
    def __init__(self,
                 Assignment_ID: Optional[int] = None,
                 Course_ID: int = None,
                 Title: str = None,
                 Description: Optional[str] = None,
                 Instructions: Optional[str] = None,
                 Due_Date: datetime = None,
                 Max_Score: float = 100.0,
                 Assignment_Type: Optional[str] = None,
                 Allowed_File_Types: Optional[str] = None,
                 Max_File_Size_MB: int = 10,
                 Created_By: Optional[int] = None,  # Instructor_ID
                 Created_At: Optional[datetime] = None,
                 Solution_Path: Optional[str] = None,  # For TA/instructor uploaded solutions
                 Solution_File_Name: Optional[str] = None,
                 Correct_Answer: Optional[str] = None,  # For AI auto-grading
                 Is_Auto_Graded: bool = False):
        self.Assignment_ID = Assignment_ID
        self.Course_ID = Course_ID
        self.Title = Title
        self.Description = Description
        self.Instructions = Instructions
        self.Due_Date = Due_Date
        self.Max_Score = Max_Score
        self.Assignment_Type = Assignment_Type
        self.Allowed_File_Types = Allowed_File_Types
        self.Max_File_Size_MB = Max_File_Size_MB
        self.Created_By = Created_By
        self.Created_At = Created_At or datetime.now()
        self.Solution_Path = Solution_Path
        self.Solution_File_Name = Solution_File_Name
        self.Correct_Answer = Correct_Answer
        self.Is_Auto_Graded = Is_Auto_Graded
    
    def to_dict(self):
        """Convert assignment to dictionary"""
        return {
            'assignment_id': self.Assignment_ID,
            'course_id': self.Course_ID,
            'title': self.Title,
            'description': self.Description,
            'instructions': self.Instructions,
            'due_date': self.Due_Date.isoformat() if self.Due_Date else None,
            'max_score': float(self.Max_Score),
            'assignment_type': self.Assignment_Type,
            'allowed_file_types': self.Allowed_File_Types,
            'max_file_size_mb': self.Max_File_Size_MB,
            'created_by': self.Created_By,
            'created_at': self.Created_At.isoformat() if self.Created_At else None,
            'solution_path': self.Solution_Path,
            'solution_file_name': self.Solution_File_Name,
            'correct_answer': self.Correct_Answer,
            'is_auto_graded': bool(self.Is_Auto_Graded)
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create assignment from dictionary"""
        due_date = None
        if data.get('Due_Date'):
            if isinstance(data['Due_Date'], str):
                due_date = datetime.fromisoformat(data['Due_Date'].replace('Z', '+00:00'))
            else:
                due_date = data['Due_Date']
        
        created_at = None
        if data.get('Created_At'):
            if isinstance(data['Created_At'], str):
                created_at = datetime.fromisoformat(data['Created_At'].replace('Z', '+00:00'))
            else:
                created_at = data['Created_At']
        
        return cls(
            Assignment_ID=data.get('Assignment_ID'),
            Course_ID=data.get('Course_ID'),
            Title=data.get('Title'),
            Description=data.get('Description'),
            Instructions=data.get('Instructions'),
            Due_Date=due_date,
            Max_Score=data.get('Max_Score', 100.0),
            Assignment_Type=data.get('Assignment_Type'),
            Allowed_File_Types=data.get('Allowed_File_Types'),
            Max_File_Size_MB=data.get('Max_File_Size_MB', 10),
            Created_By=data.get('Created_By'),
            Created_At=created_at,
            Solution_Path=data.get('Solution_Path'),
            Solution_File_Name=data.get('Solution_File_Name'),
            Correct_Answer=data.get('Correct_Answer'),
            Is_Auto_Graded=data.get('Is_Auto_Graded', False)
        )
