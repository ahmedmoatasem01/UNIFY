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
            cursor.execute("""
                SELECT m.Message_ID, m.Sender_ID, m.Receiver_ID, m.Message_Text, m.Timestamp, m.Is_Read,
                       u1.Username as Sender_Name, u2.Username as Receiver_Name
                FROM `Message` m
                LEFT JOIN `User` u1 ON m.Sender_ID = u1.User_ID
                LEFT JOIN `User` u2 ON m.Receiver_ID = u2.User_ID
            """)
            rows = cursor.fetchall()
            messages = []
            for row in rows:
                messages.append(Message(
                    Message_ID=row[0],
                    Sender_ID=row[1],
                    Receiver_ID=row[2],
                    Message_Text=row[3],
                    Timestamp=row[4],
                    Is_Read=bool(row[5]) if row[5] is not None else False,
                    Sender_Name=row[6],
                    Receiver_Name=row[7]
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
            cursor.execute("""
                SELECT m.Message_ID, m.Sender_ID, m.Receiver_ID, m.Message_Text, m.Timestamp, m.Is_Read,
                       u1.Username as Sender_Name, u2.Username as Receiver_Name
                FROM `Message` m
                LEFT JOIN `User` u1 ON m.Sender_ID = u1.User_ID
                LEFT JOIN `User` u2 ON m.Receiver_ID = u2.User_ID
                WHERE m.Message_ID = %s
            """, (message_id,))
            row = cursor.fetchone()
            if row:
                return Message(
                    Message_ID=row[0],
                    Sender_ID=row[1],
                    Receiver_ID=row[2],
                    Message_Text=row[3],
                    Timestamp=row[4],
                    Is_Read=bool(row[5]) if row[5] is not None else False,
                    Sender_Name=row[6],
                    Receiver_Name=row[7]
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
                """SELECT m.Message_ID, m.Sender_ID, m.Receiver_ID, m.Message_Text, m.Timestamp, m.Is_Read,
                          u1.Username as Sender_Name, u2.Username as Receiver_Name
                   FROM `Message` m
                   LEFT JOIN `User` u1 ON m.Sender_ID = u1.User_ID
                   LEFT JOIN `User` u2 ON m.Receiver_ID = u2.User_ID
                   WHERE (m.Sender_ID = %s AND m.Receiver_ID = %s) OR (m.Sender_ID = %s AND m.Receiver_ID = %s)
                   ORDER BY m.Timestamp ASC""",
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
                    Timestamp=row[4],
                    Is_Read=bool(row[5]) if row[5] is not None else False,
                    Sender_Name=row[6],
                    Receiver_Name=row[7]
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
            cursor.execute("""
                SELECT m.Message_ID, m.Sender_ID, m.Receiver_ID, m.Message_Text, m.Timestamp, m.Is_Read,
                       u1.Username as Sender_Name, u2.Username as Receiver_Name
                FROM `Message` m
                LEFT JOIN `User` u1 ON m.Sender_ID = u1.User_ID
                LEFT JOIN `User` u2 ON m.Receiver_ID = u2.User_ID
                WHERE m.Receiver_ID = %s 
                ORDER BY m.Timestamp DESC
            """, (receiver_id,))
            rows = cursor.fetchall()
            messages = []
            for row in rows:
                messages.append(Message(
                    Message_ID=row[0],
                    Sender_ID=row[1],
                    Receiver_ID=row[2],
                    Message_Text=row[3],
                    Timestamp=row[4],
                    Is_Read=bool(row[5]) if row[5] is not None else False,
                    Sender_Name=row[6],
                    Receiver_Name=row[7]
                ))
            return messages
        finally:
            cursor.close()
            conn.close()
    
    def get_by_recipient_id(self, recipient_id):
        """Get all messages for a recipient (alias for get_by_receiver)"""
        return self.get_by_receiver(recipient_id)

    def get_user_conversations(self, user_id):
        """Get list of users that current user has conversations with"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT 
                    CASE 
                        WHEN m.Sender_ID = %s THEN m.Receiver_ID 
                        ELSE m.Sender_ID 
                    END as Other_User_ID,
                    CASE 
                        WHEN m.Sender_ID = %s THEN u2.Username 
                        ELSE u1.Username 
                    END as Other_User_Name,
                    MAX(m.Timestamp) as Last_Message_Time,
                    (SELECT m2.Message_Text 
                     FROM `Message` m2 
                     WHERE (m2.Sender_ID = %s AND m2.Receiver_ID = CASE WHEN m.Sender_ID = %s THEN m.Receiver_ID ELSE m.Sender_ID END)
                        OR (m2.Receiver_ID = %s AND m2.Sender_ID = CASE WHEN m.Sender_ID = %s THEN m.Receiver_ID ELSE m.Sender_ID END)
                     ORDER BY m2.Timestamp DESC LIMIT 1) as Last_Message,
                    (SELECT COUNT(*) 
                     FROM `Message` m3 
                     WHERE m3.Receiver_ID = %s 
                       AND m3.Sender_ID = CASE WHEN m.Sender_ID = %s THEN m.Receiver_ID ELSE m.Sender_ID END
                       AND m3.Is_Read = 0) as Unread_Count
                FROM `Message` m
                LEFT JOIN `User` u1 ON m.Sender_ID = u1.User_ID
                LEFT JOIN `User` u2 ON m.Receiver_ID = u2.User_ID
                WHERE m.Sender_ID = %s OR m.Receiver_ID = %s
                GROUP BY Other_User_ID, Other_User_Name
                ORDER BY Last_Message_Time DESC
            """, (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id))
            rows = cursor.fetchall()
            conversations = []
            for row in rows:
                conversations.append({
                    'User_ID': row[0],
                    'Username': row[1],
                    'Last_Message_Time': row[2],
                    'Last_Message': row[3],
                    'Unread_Count': row[4] or 0
                })
            return conversations
        finally:
            cursor.close()
            conn.close()

    def get_unread_count(self, user_id):
        """Get count of unread messages for a user"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM `Message` 
                WHERE Receiver_ID = %s AND Is_Read = 0
            """, (user_id,))
            row = cursor.fetchone()
            return row[0] if row else 0
        finally:
            cursor.close()
            conn.close()

    def mark_as_read(self, message_id):
        """Mark a message as read"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE `Message` 
                SET Is_Read = 1 
                WHERE Message_ID = %s
            """, (message_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def mark_conversation_as_read(self, receiver_id, sender_id):
        """Mark all messages from a sender to receiver as read"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE `Message` 
                SET Is_Read = 1 
                WHERE Receiver_ID = %s AND Sender_ID = %s AND Is_Read = 0
            """, (receiver_id, sender_id))
            conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conn.close()

    def create(self, message):
        """Create a new message"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO `Message` (Sender_ID, Receiver_ID, Message_Text, Timestamp, Is_Read) VALUES (%s, %s, %s, %s, %s)",
                (message.Sender_ID, message.Receiver_ID, message.Message_Text, message.Timestamp, message.Is_Read)
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

