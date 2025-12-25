"""
Advisor Conversation Repository
Handles database operations for advisor conversations
"""
from models.advisor_conversation import AdvisorConversation
from core.db_singleton import DatabaseConnection
from datetime import datetime


class AdvisorConversationRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()
        self.db = DatabaseConnection.get_instance()
    
    def create_table(self):
        """Create advisor conversation table if it doesn't exist"""
        try:
            query = """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AdvisorConversation' AND xtype='U')
            CREATE TABLE AdvisorConversation (
                Conversation_ID INT IDENTITY(1,1) PRIMARY KEY,
                Student_ID INT NOT NULL,
                Conversation_Type NVARCHAR(50),
                Started_At DATETIME DEFAULT GETDATE(),
                Last_Message_At DATETIME,
                Status NVARCHAR(20) CHECK (Status IN ('active', 'resolved', 'escalated', 'archived')) DEFAULT 'active',
                Escalated_To_Advisor_ID INT,
                FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
                FOREIGN KEY (Escalated_To_Advisor_ID) REFERENCES Instructor(Instructor_ID)
            )
            """
            self.db.execute_update(query)
        except Exception as e:
            print(f"Error creating AdvisorConversation table: {e}")
            import traceback
            traceback.print_exc()
    
    def create(self, conversation):
        """Create a new conversation"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO AdvisorConversation (Student_ID, Conversation_Type, Started_At, Last_Message_At, Status, Escalated_To_Advisor_ID)
            OUTPUT INSERTED.Conversation_ID
            VALUES (?, ?, ?, ?, ?, ?)
            """
            started_at = conversation.Started_At or datetime.now()
            cursor.execute(
                query,
                (conversation.Student_ID, conversation.Conversation_Type, started_at,
                 conversation.Last_Message_At, conversation.Status, conversation.Escalated_To_Advisor_ID)
            )
            row = cursor.fetchone()
            if row:
                conversation.Conversation_ID = row[0]
            conn.commit()
            return conversation
        finally:
            cursor.close()
            conn.close()
    
    def get_by_id(self, conversation_id):
        """Get conversation by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Conversation_ID, Student_ID, Conversation_Type, Started_At, Last_Message_At, Status, Escalated_To_Advisor_ID "
                "FROM AdvisorConversation WHERE Conversation_ID = ?",
                (conversation_id,)
            )
            row = cursor.fetchone()
            if row:
                return self._map_to_object(row)
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_by_student(self, student_id):
        """Get all conversations for a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Conversation_ID, Student_ID, Conversation_Type, Started_At, Last_Message_At, Status, Escalated_To_Advisor_ID "
                "FROM AdvisorConversation WHERE Student_ID = ? ORDER BY Last_Message_At DESC, Started_At DESC",
                (student_id,)
            )
            rows = cursor.fetchall()
            return [self._map_to_object(row) for row in rows] if rows else []
        finally:
            cursor.close()
            conn.close()
    
    def get_active_by_student(self, student_id):
        """Get active conversations for a student"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Conversation_ID, Student_ID, Conversation_Type, Started_At, Last_Message_At, Status, Escalated_To_Advisor_ID "
                "FROM AdvisorConversation WHERE Student_ID = ? AND Status = 'active' ORDER BY Last_Message_At DESC",
                (student_id,)
            )
            rows = cursor.fetchall()
            return [self._map_to_object(row) for row in rows] if rows else []
        finally:
            cursor.close()
            conn.close()
    
    def update(self, conversation):
        """Update a conversation"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE AdvisorConversation SET Conversation_Type = ?, Last_Message_At = ?, Status = ?, Escalated_To_Advisor_ID = ? WHERE Conversation_ID = ?",
                (conversation.Conversation_Type, conversation.Last_Message_At, conversation.Status,
                 conversation.Escalated_To_Advisor_ID, conversation.Conversation_ID)
            )
            conn.commit()
            return conversation
        finally:
            cursor.close()
            conn.close()
    
    def update_last_message_at(self, conversation_id):
        """Update last message timestamp"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE AdvisorConversation SET Last_Message_At = GETDATE() WHERE Conversation_ID = ?",
                (conversation_id,)
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def _map_to_object(self, row):
        """Map database row to AdvisorConversation object"""
        if not row:
            return None
        return AdvisorConversation(
            Conversation_ID=row[0],
            Student_ID=row[1],
            Conversation_Type=row[2],
            Started_At=row[3],
            Last_Message_At=row[4],
            Status=row[5],
            Escalated_To_Advisor_ID=row[6] if len(row) > 6 else None
        )
