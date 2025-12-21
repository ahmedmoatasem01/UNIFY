"""
Knowledge Base Repository
Handles database operations for knowledge base documents
"""
from models.knowledge_base import KnowledgeBase
from core.db_singleton import DatabaseConnection
from datetime import datetime

class KnowledgeBaseRepository:
    def __init__(self):
        self.db = DatabaseConnection.get_instance()
    
    def create_table(self):
        """Create knowledge base table if it doesn't exist"""
        query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Knowledge_Base' AND xtype='U')
        CREATE TABLE Knowledge_Base (
            KB_ID INT IDENTITY(1,1) PRIMARY KEY,
            Title NVARCHAR(500) NOT NULL,
            Content NVARCHAR(MAX) NOT NULL,
            Category NVARCHAR(100),
            Keywords NVARCHAR(500),
            Created_Date DATETIME DEFAULT GETDATE(),
            Updated_Date DATETIME DEFAULT GETDATE(),
            Source NVARCHAR(500)
        )
        """
        self.db.execute_update(query)
    
    def add(self, knowledge_base):
        """Add a new knowledge base document"""
        query = """
        INSERT INTO Knowledge_Base (Title, Content, Category, Keywords, Source)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (
            knowledge_base.Title,
            knowledge_base.Content,
            knowledge_base.Category,
            knowledge_base.Keywords,
            knowledge_base.Source
        )
        return self.db.execute_update(query, params)
    
    def get_by_id(self, kb_id):
        """Get a knowledge base document by ID"""
        query = "SELECT * FROM Knowledge_Base WHERE KB_ID = ?"
        result = self.db.fetch_one(query, (kb_id,))
        return self._map_to_object(result) if result else None
    
    def get_all(self):
        """Get all knowledge base documents"""
        query = "SELECT * FROM Knowledge_Base ORDER BY Created_Date DESC"
        results = self.db.fetch_all(query)
        return [self._map_to_object(row) for row in results] if results else []
    
    def search(self, search_term, limit=5):
        """Search knowledge base by keywords, title, or content"""
        query = """
        SELECT * FROM Knowledge_Base
        WHERE Title LIKE ? OR Content LIKE ? OR Keywords LIKE ?
        ORDER BY 
            CASE 
                WHEN Title LIKE ? THEN 1
                WHEN Keywords LIKE ? THEN 2
                ELSE 3
            END,
            Created_Date DESC
        OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY
        """
        search_pattern = f"%{search_term}%"
        params = (search_pattern, search_pattern, search_pattern, 
                 search_pattern, search_pattern, limit)
        results = self.db.fetch_all(query, params)
        return [self._map_to_object(row) for row in results] if results else []
    
    def search_by_category(self, category):
        """Get all documents in a category"""
        query = "SELECT * FROM Knowledge_Base WHERE Category = ? ORDER BY Created_Date DESC"
        results = self.db.fetch_all(query, (category,))
        return [self._map_to_object(row) for row in results] if results else []
    
    def update(self, knowledge_base):
        """Update a knowledge base document"""
        query = """
        UPDATE Knowledge_Base
        SET Title = ?, Content = ?, Category = ?, Keywords = ?, 
            Updated_Date = ?, Source = ?
        WHERE KB_ID = ?
        """
        params = (
            knowledge_base.Title,
            knowledge_base.Content,
            knowledge_base.Category,
            knowledge_base.Keywords,
            datetime.now(),
            knowledge_base.Source,
            knowledge_base.KB_ID
        )
        return self.db.execute_update(query, params)
    
    def delete(self, kb_id):
        """Delete a knowledge base document"""
        query = "DELETE FROM Knowledge_Base WHERE KB_ID = ?"
        return self.db.execute_update(query, (kb_id,))
    
    def get_categories(self):
        """Get all unique categories"""
        query = "SELECT DISTINCT Category FROM Knowledge_Base WHERE Category IS NOT NULL"
        results = self.db.fetch_all(query)
        return [row[0] for row in results] if results else []
    
    def _map_to_object(self, row):
        """Map database row to KnowledgeBase object"""
        if not row:
            return None
        return KnowledgeBase(
            kb_id=row[0],
            title=row[1],
            content=row[2],
            category=row[3] if len(row) > 3 else None,
            keywords=row[4] if len(row) > 4 else None,
            created_date=row[5] if len(row) > 5 else None,
            updated_date=row[6] if len(row) > 6 else None,
            source=row[7] if len(row) > 7 else None
        )
