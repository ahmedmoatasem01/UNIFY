"""
Course Material Model
Represents course materials uploaded by instructors (PDFs, PowerPoints, videos, links, etc.)
"""
from datetime import datetime
from typing import Optional


class CourseMaterial:
    def __init__(
        self,
        Material_ID: Optional[int] = None,
        Course_ID: int = 0,
        Instructor_ID: int = 0,
        Material_Title: str = "",
        Material_Type: str = "other",  # pdf, pptx, video, assignment, link, other
        File_Path: Optional[str] = None,
        Link_URL: Optional[str] = None,
        Description: Optional[str] = None,
        Week_Number: Optional[int] = None,
        Topic: Optional[str] = None,
        Upload_Date: Optional[datetime] = None,
        File_Size: Optional[int] = None,
        Download_Count: int = 0,
        Is_Active: bool = True,
        **kwargs
    ):
        self.Material_ID = Material_ID
        self.Course_ID = Course_ID
        self.Instructor_ID = Instructor_ID
        self.Material_Title = Material_Title
        self.Material_Type = Material_Type
        self.File_Path = File_Path
        self.Link_URL = Link_URL
        self.Description = Description
        self.Week_Number = Week_Number
        self.Topic = Topic
        self.Upload_Date = Upload_Date or datetime.now()
        self.File_Size = File_Size
        self.Download_Count = Download_Count
        self.Is_Active = Is_Active
        
        # Handle any additional fields passed via kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<CourseMaterial(Material_ID={self.Material_ID}, Course_ID={self.Course_ID}, Title='{self.Material_Title}', Type='{self.Material_Type}')>"
    
    def to_dict(self):
        """Convert course material to dictionary"""
        return {
            'Material_ID': self.Material_ID,
            'Course_ID': self.Course_ID,
            'Instructor_ID': self.Instructor_ID,
            'Material_Title': self.Material_Title,
            'Material_Type': self.Material_Type,
            'File_Path': self.File_Path,
            'Link_URL': self.Link_URL,
            'Description': self.Description,
            'Week_Number': self.Week_Number,
            'Topic': self.Topic,
            'Upload_Date': self.Upload_Date.isoformat() if isinstance(self.Upload_Date, datetime) else self.Upload_Date,
            'File_Size': self.File_Size,
            'Download_Count': self.Download_Count,
            'Is_Active': self.Is_Active,
            'file_url': f'/course-materials/download/{self.Material_ID}' if self.File_Path else None,
            'is_link': self.Material_Type == 'link' or self.Link_URL is not None
        }
    
    def get_file_extension(self):
        """Get file extension from file path"""
        if not self.File_Path:
            return None
        return self.File_Path.split('.')[-1].lower() if '.' in self.File_Path else None
    
    def is_previewable(self):
        """Check if file can be previewed in browser"""
        previewable_types = ['pdf', 'link']
        previewable_extensions = ['pdf', 'txt', 'jpg', 'jpeg', 'png', 'gif']
        if self.Material_Type in previewable_types:
            return True
        ext = self.get_file_extension()
        return ext in previewable_extensions if ext else False

