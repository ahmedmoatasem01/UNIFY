"""
Knowledge Base Model
Stores documents/information for RAG retrieval
"""

class KnowledgeBase:
    def __init__(self, kb_id=None, title=None, content=None, category=None, 
                 keywords=None, created_date=None, updated_date=None, source=None):
        self.KB_ID = kb_id
        self.Title = title
        self.Content = content
        self.Category = category
        self.Keywords = keywords  # Comma-separated keywords for search
        self.Created_Date = created_date
        self.Updated_Date = updated_date
        self.Source = source
    
    def to_dict(self):
        return {
            'KB_ID': self.KB_ID,
            'Title': self.Title,
            'Content': self.Content,
            'Category': self.Category,
            'Keywords': self.Keywords,
            'Created_Date': self.Created_Date,
            'Updated_Date': self.Updated_Date,
            'Source': self.Source
        }
    
    def __repr__(self):
        return f"<KnowledgeBase {self.KB_ID}: {self.Title}>"
