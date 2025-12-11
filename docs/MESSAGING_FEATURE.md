# Messaging Feature Documentation

## Overview
The UNIFY in-app messaging system enables secure communication between users (students, teaching assistants, instructors, and administrators) within the platform.

## Features

### Core Functionality
- ✅ **Real-time Messaging**: Send and receive messages instantly
- ✅ **Conversation Management**: View all conversations in one place
- ✅ **Unread Indicators**: Track unread messages with visual badges
- ✅ **Message Search**: Search through conversations
- ✅ **New Conversations**: Start conversations with any user
- ✅ **Auto-refresh**: Messages refresh automatically every 5 seconds
- ✅ **Responsive Design**: Works on desktop and mobile devices

### User Experience
- Clean, modern interface matching UNIFY design system
- Real-time message updates
- Conversation sorting by most recent activity
- Message timestamps (relative and absolute)
- Typing area with auto-resize
- Empty state guidance for new users

## Architecture

### Backend Components

#### 1. Model (`src/models/message.py`)
```python
class Message:
    - Message_ID: Unique identifier
    - Sender_ID: User who sent the message
    - Receiver_ID: User who receives the message
    - Message_Text: Content of the message
    - Timestamp: When the message was sent
    - Is_Read: Whether the message has been read
    - Sender_Name: Display name of sender (optional)
    - Receiver_Name: Display name of receiver (optional)
```

#### 2. Repository (`src/repositories/message.repository.py`)
**Methods:**
- `get_all()` - Get all messages
- `get_by_id(message_id)` - Get specific message
- `get_conversation(user1_id, user2_id)` - Get conversation between two users
- `get_by_receiver(receiver_id)` - Get all messages for a receiver
- `get_user_conversations(user_id)` - Get list of all conversations for a user
- `get_unread_count(user_id)` - Get count of unread messages
- `mark_as_read(message_id)` - Mark single message as read
- `mark_conversation_as_read(receiver_id, sender_id)` - Mark all messages in conversation as read
- `create(message)` - Send a new message
- `delete(message_id)` - Delete a message

#### 3. Controller (`src/controllers/message_controller.py`)
**API Endpoints:**
- `GET /messages/` - Render messages page
- `GET /messages/api/conversations` - Get all conversations for current user
- `GET /messages/api/conversation/<user_id>` - Get conversation with specific user
- `POST /messages/api/send` - Send a new message
- `GET /messages/api/unread-count` - Get unread message count
- `POST /messages/api/mark-read/<message_id>` - Mark message as read
- `GET /messages/api/users` - Get all users for starting new conversations

### Frontend Components

#### 1. HTML Template (`src/templates/messages.html`)
- Sidebar navigation
- Conversations list panel
- Chat window
- New message modal
- Empty states

#### 2. JavaScript (`src/static/scripts/messages.js`)
**Key Functions:**
- `loadConversations()` - Load and display conversation list
- `loadConversation(userId, username)` - Load messages for specific conversation
- `handleSendMessage()` - Send message from chat window
- `sendNewMessage()` - Send message from new message modal
- `startPolling()` - Auto-refresh messages every 5 seconds
- `formatTime()` - Format timestamps for display

#### 3. CSS (`src/static/styles/messages.css`)
- Modern, clean design
- Responsive layout
- Dark mode support
- Smooth animations
- Consistent with UNIFY design system

## Database Schema

### Message Table
```sql
CREATE TABLE Message (
    Message_ID INT AUTO_INCREMENT PRIMARY KEY,
    Sender_ID INT NOT NULL,
    Receiver_ID INT NOT NULL,
    Message_Text TEXT NOT NULL,
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Is_Read TINYINT(1) DEFAULT 0,
    CONSTRAINT FK_Message_Sender FOREIGN KEY (Sender_ID)
        REFERENCES User(User_ID) ON DELETE CASCADE,
    CONSTRAINT FK_Message_Receiver FOREIGN KEY (Receiver_ID)
        REFERENCES User(User_ID) ON DELETE CASCADE,
    INDEX idx_sender_id (Sender_ID),
    INDEX idx_receiver_id (Receiver_ID),
    INDEX idx_timestamp (Timestamp),
    INDEX idx_is_read (Is_Read)
);
```

## Installation & Setup

### 1. Database Migration
If you have an existing database, run the migration:
```bash
mysql -u root -p unify < src/database/add_is_read_column.sql
```

For new installations, the schema includes Is_Read column by default.

### 2. Verify Installation
1. Start your Flask application
2. Login to UNIFY
3. Navigate to Messages page
4. You should see the messaging interface

## Usage Guide

### For Users

#### Viewing Conversations
1. Click on "Messages" in the sidebar
2. All your conversations appear in the left panel
3. Click on any conversation to view messages

#### Sending a Message
**To existing conversation:**
1. Select a conversation
2. Type your message in the input box at the bottom
3. Press Enter or click the send button

**To start a new conversation:**
1. Click the "+" button in conversations header
2. Select a recipient from the dropdown
3. Type your message
4. Click "Send"

#### Managing Messages
- **Search**: Use the search box to filter conversations
- **Unread**: Unread messages are indicated with blue badges
- **Auto-refresh**: Messages update automatically every 5 seconds

## API Reference

### Send Message
```http
POST /messages/api/send
Content-Type: application/json

{
  "receiver_id": 2,
  "message_text": "Hello, how are you?"
}

Response: 201 Created
{
  "Message_ID": 123,
  "Sender_ID": 1,
  "Receiver_ID": 2,
  "Message_Text": "Hello, how are you?",
  "Timestamp": "2025-12-11T10:30:00",
  "Is_Read": false
}
```

### Get Conversations
```http
GET /messages/api/conversations

Response: 200 OK
[
  {
    "User_ID": 2,
    "Username": "john_doe",
    "Last_Message_Time": "2025-12-11T10:30:00",
    "Last_Message": "Hello, how are you?",
    "Unread_Count": 3
  }
]
```

### Get Conversation Messages
```http
GET /messages/api/conversation/2

Response: 200 OK
[
  {
    "Message_ID": 123,
    "Sender_ID": 1,
    "Receiver_ID": 2,
    "Message_Text": "Hello!",
    "Timestamp": "2025-12-11T10:30:00",
    "Is_Read": true,
    "Sender_Name": "alice_smith",
    "Receiver_Name": "john_doe"
  }
]
```

## Security Features

### Authentication
- All messaging endpoints require user authentication
- Session-based authentication using Flask sessions
- Unauthorized requests return 401 status

### Data Validation
- Message text cannot be empty
- Receiver ID must be valid
- SQL injection protection via parameterized queries

### Privacy
- Users can only view their own conversations
- Messages are only visible to sender and receiver
- Cascade delete: Messages deleted when user is deleted

## Performance Optimization

### Database Indexes
- `idx_sender_id` - Fast lookups by sender
- `idx_receiver_id` - Fast lookups by receiver
- `idx_timestamp` - Efficient sorting by time
- `idx_is_read` - Quick unread message queries

### Frontend Optimization
- Polling interval: 5 seconds (configurable)
- Conversation caching
- Lazy loading of messages
- Automatic scroll to latest message

## Troubleshooting

### Messages not loading
1. Check if user is logged in
2. Verify database connection
3. Check browser console for errors
4. Ensure Message table exists with Is_Read column

### Messages not sending
1. Verify receiver_id is valid
2. Check message text is not empty
3. Ensure user is authenticated
4. Check server logs for errors

### Styling issues
1. Clear browser cache
2. Verify messages.css is loaded
3. Check for CSS conflicts

## Future Enhancements

### Potential Features
- [ ] File attachments
- [ ] Image sharing
- [ ] Group messaging
- [ ] Message reactions
- [ ] Message editing/deletion
- [ ] Read receipts
- [ ] Typing indicators
- [ ] Push notifications
- [ ] WebSocket for real-time updates
- [ ] Message encryption
- [ ] Voice messages
- [ ] Video calls

## Technical Details

### Dependencies
- Flask (web framework)
- MySQL (database)
- mysql-connector-python (database driver)

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### File Structure
```
src/
├── models/
│   └── message.py                 # Message data model
├── repositories/
│   └── message.repository.py      # Database operations
├── controllers/
│   └── message_controller.py      # API endpoints
├── templates/
│   └── messages.html              # Main UI template
├── static/
│   ├── scripts/
│   │   └── messages.js            # Frontend logic
│   └── styles/
│       └── messages.css           # Styling
└── database/
    ├── schema.sql                 # Complete schema
    └── add_is_read_column.sql     # Migration script
```

## Support

For issues or questions:
1. Check this documentation
2. Review code comments
3. Check Flask/MySQL documentation
4. Contact CSAI 203 Team 5

---

**Last Updated**: December 11, 2025  
**Version**: 1.0  
**Team**: CSAI 203 - Team 5
