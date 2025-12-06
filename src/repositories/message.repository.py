from core.db_singleton import DatabaseConnection
from models.message import Message


class MessageRepository:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_all(self):
        """Get all messages"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Message_ID, Sender_ID, Receiver_ID, Message_Text, Timestamp FROM `Message`")
            rows = cursor.fetchall()
            messages = []
            for row in rows:
                messages.append(Message(
                    Message_ID=row[0],
                    Sender_ID=row[1],
                    Receiver_ID=row[2],
                    Message_Text=row[3],
                    Timestamp=row[4]
                ))
            return messages
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, message_id):
        """Get message by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Message_ID, Sender_ID, Receiver_ID, Message_Text, Timestamp FROM `Message` WHERE Message_ID = %s", (message_id,))
            row = cursor.fetchone()
            if row:
                return Message(
                    Message_ID=row[0],
                    Sender_ID=row[1],
                    Receiver_ID=row[2],
                    Message_Text=row[3],
                    Timestamp=row[4]
                )
            return None
        finally:
            cursor.close()
            conn.close()

    def get_conversation(self, user1_id, user2_id):
        """Get conversation between two users"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT Message_ID, Sender_ID, Receiver_ID, Message_Text, Timestamp 
                   FROM `Message` 
                   WHERE (Sender_ID = %s AND Receiver_ID = %s) OR (Sender_ID = %s AND Receiver_ID = %s)
                   ORDER BY Timestamp""",
                (user1_id, user2_id, user2_id, user1_id)
            )
            rows = cursor.fetchall()
            messages = []
            for row in rows:
                messages.append(Message(
                    Message_ID=row[0],
                    Sender_ID=row[1],
                    Receiver_ID=row[2],
                    Message_Text=row[3],
                    Timestamp=row[4]
                ))
            return messages
        finally:
            cursor.close()
            conn.close()

    def get_by_receiver(self, receiver_id):
        """Get all messages for a receiver"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Message_ID, Sender_ID, Receiver_ID, Message_Text, Timestamp FROM `Message` WHERE Receiver_ID = %s ORDER BY Timestamp DESC", (receiver_id,))
            rows = cursor.fetchall()
            messages = []
            for row in rows:
                messages.append(Message(
                    Message_ID=row[0],
                    Sender_ID=row[1],
                    Receiver_ID=row[2],
                    Message_Text=row[3],
                    Timestamp=row[4]
                ))
            return messages
        finally:
            cursor.close()
            conn.close()
    
    def get_by_recipient_id(self, recipient_id):
        """Get all messages for a recipient (alias for get_by_receiver)"""
        return self.get_by_receiver(recipient_id)

    def create(self, message):
        """Create a new message"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO `Message` (Sender_ID, Receiver_ID, Message_Text, Timestamp) VALUES (%s, %s, %s, %s)",
                (message.Sender_ID, message.Receiver_ID, message.Message_Text, message.Timestamp)
            )
            conn.commit()
            message.Message_ID = cursor.lastrowid
            return message
        finally:
            cursor.close()
            conn.close()

    def delete(self, message_id):
        """Delete a message by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM `Message` WHERE Message_ID = %s", (message_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

