class AINote:
    def __init__(self, Note_ID=None, Student_ID=None, Original_File=None, Summary_Text=None, Upload_Date=None):
        self.Note_ID = Note_ID
        self.Student_ID = Student_ID
        self.Original_File = Original_File
        self.Summary_Text = Summary_Text
        self.Upload_Date = Upload_Date

    def to_dict(self):
        """Convert AINote to dictionary"""
        return {
            'Note_ID': self.Note_ID,
            'Student_ID': self.Student_ID,
            'Original_File': self.Original_File,
            'Summary_Text': self.Summary_Text,
            'Upload_Date': self.Upload_Date.isoformat() if hasattr(self.Upload_Date, 'isoformat') else str(self.Upload_Date) if self.Upload_Date else None
        }