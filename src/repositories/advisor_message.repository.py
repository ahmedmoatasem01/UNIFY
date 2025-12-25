"""
Advisor Message Repository
Handles database operations for advisor messages
"""
from models.advisor_message import AdvisorMessage
from core.db_singleton import DatabaseConnection
from datetime import datetime


class AdvisorMessageRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()
        self.db = DatabaseConnection.get_instance()
    
    def create_table(self):
        """Create advisor message table if it doesn't exist"""
        try:
            query = """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AdvisorMessage' AND xtype='U')
            CREATE TABLE AdvisorMessage (
                Message_ID INT IDENTITY(1,1) PRIMARY KEY,
                Conversation_ID INT NOT NULL,
                Sender_Type NVARCHAR(20) CHECK (Sender_Type IN ('student', 'ai', 'advisor')),
                Message_Text NVARCHAR(MAX) NOT NULL,
                Intent NVARCHAR(100),
                Confidence_Score DECIMAL(3,2),
                Sent_At DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (Conversation_ID) REFERENCES AdvisorConversation(Conversation_ID)
            )
            """
            self.db.execute_update(query)
        except Exception as e:
            print(f"Error creating AdvisorMessage table: {e}")
            import traceback
            traceback.print_exc()
    
    def create(self, message):
        """Create a new message"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO AdvisorMessage (Conversation_ID, Sender_Type, Message_Text, Intent, Confidence_Score, Sent_At)
            OUTPUT INSERTED.Message_ID
            VALUES (?, ?, ?, ?, ?, ?)
            """
            sent_at = message.Sent_At or datetime.now()
            cursor.execute(
                query,
                (message.Conversation_ID, message.Sender_Type, message.Message_Text,
                 message.Intent, message.Confidence_Score, sent_at)
            )
            row = cursor.fetchone()
            if row:
                message.Message_ID = row[0]
                message.Sent_At = sent_at
            conn.commit()
            return message
        finally:
            cursor.close()
            conn.close()
    
    def get_by_id(self, message_id):
        """Get message by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Message_ID, Conversation_ID, Sender_Type, Message_Text, Intent, Confidence_Score, Sent_At "
                "FROM AdvisorMessage WHERE Message_ID = ?",
                (message_id,)
            )
            row = cursor.fetchone()
            if row:
                return self._map_to_object(row)
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_by_conversation(self, conversation_id):
        """Get all messages for a conversation"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Message_ID, Conversation_ID, Sender_Type, Message_Text, Intent, Confidence_Score, Sent_At "
                "FROM AdvisorMessage WHERE Conversation_ID = ? ORDER BY Sent_At ASC",
                (conversation_id,)
            )
            rows = cursor.fetchall()
            return [self._map_to_object(row) for row in rows] if rows else []
        finally:
            cursor.close()
            conn.close()
    
    def get_latest_by_conversation(self, conversation_id, limit=10):
        """Get latest messages for a conversation"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT TOP (?)
                Message_ID, Conversation_ID, Sender_Type, Message_Text, Intent, Confidence_Score, Sent_At
                FROM AdvisorMessage 
                WHERE Conversation_ID = ? 
                ORDER BY Sent_At DESC
                """,
                (limit, conversation_id)
            )
            rows = cursor.fetchall()
            # Reverse to get chronological order
            messages = [self._map_to_object(row) for row in reversed(rows)] if rows else []
            return messages
        finally:
            cursor.close()
            conn.close()
    
    def _map_to_object(self, row):
        """Map database row to AdvisorMessage object"""
        if not row:
            return None
        return AdvisorMessage(
            Message_ID=row[0],
            Conversation_ID=row[1],
            Sender_Type=row[2],
            Message_Text=row[3],
            Intent=row[4] if len(row) > 4 and row[4] else None,
            Confidence_Score=float(row[5]) if len(row) > 5 and row[5] is not None else None,
            Sent_At=row[6] if len(row) > 6 else None
        )
