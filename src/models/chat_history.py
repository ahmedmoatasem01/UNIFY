"""
Chat History Model
Stores conversation history between user and AI Assistant
"""

class ChatHistory:
    def __init__(self, chat_id=None, user_id=None, question=None, 
                 answer=None, sources=None, created_date=None):
        self.Chat_ID = chat_id
        self.User_ID = user_id
        self.Question = question
        self.Answer = answer
        self.Sources = sources  # JSON string of source KB_IDs
        self.Created_Date = created_date
    
    def to_dict(self):
        return {
            'Chat_ID': self.Chat_ID,
            'User_ID': self.User_ID,
            'Question': self.Question,
            'Answer': self.Answer,
            'Sources': self.Sources,
            'Created_Date': self.Created_Date
        }
    
    def __repr__(self):
        return f"<ChatHistory {self.Chat_ID}: {self.Question[:50]}...>"
