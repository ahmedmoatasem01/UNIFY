"""
Chat History Repository
Handles database operations for chat history
"""
from models.chat_history import ChatHistory
from core.db_singleton import DatabaseConnection

class ChatHistoryRepository:
    def __init__(self):
        self.db = DatabaseConnection.get_instance()
    
    def create_table(self):
        """Create chat history table if it doesn't exist"""
        query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Chat_History' AND xtype='U')
        CREATE TABLE Chat_History (
            Chat_ID INT IDENTITY(1,1) PRIMARY KEY,
            User_ID INT NOT NULL,
            Question NVARCHAR(MAX) NOT NULL,
            Answer NVARCHAR(MAX) NOT NULL,
            Sources NVARCHAR(MAX),
            Created_Date DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (User_ID) REFERENCES [User](User_ID)
        )
        """
        self.db.execute_update(query)
    
    def add(self, chat_history):
        """Add a new chat history entry"""
        query = """
        INSERT INTO Chat_History (User_ID, Question, Answer, Sources)
        VALUES (?, ?, ?, ?)
        """
        params = (
            chat_history.User_ID,
            chat_history.Question,
            chat_history.Answer,
            chat_history.Sources
        )
        return self.db.execute_update(query, params)
    
    def get_by_user_id(self, user_id, limit=50):
        """Get chat history for a user"""
        query = """
        SELECT * FROM Chat_History
        WHERE User_ID = ?
        ORDER BY Created_Date DESC
        OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY
        """
        results = self.db.fetch_all(query, (user_id, limit))
        return [self._map_to_object(row) for row in results] if results else []
    
    def get_recent_chats(self, user_id, limit=10):
        """Get recent chat history for a user"""
        return self.get_by_user_id(user_id, limit)
    
    def delete_by_user(self, user_id):
        """Delete all chat history for a user"""
        query = "DELETE FROM Chat_History WHERE User_ID = ?"
        return self.db.execute_update(query, (user_id,))
    
    def _map_to_object(self, row):
        """Map database row to ChatHistory object"""
        if not row:
            return None
        return ChatHistory(
            chat_id=row[0],
            user_id=row[1],
            question=row[2],
            answer=row[3],
            sources=row[4] if len(row) > 4 else None,
            created_date=row[5] if len(row) > 5 else None
        )
