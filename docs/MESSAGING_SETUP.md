# Messaging Feature - Quick Setup Guide

## Prerequisites
- UNIFY application installed and running
- MySQL database configured
- User authentication system working

## Installation Steps

### Step 1: Update Database Schema

**Option A: New Installation**
If you're setting up the database for the first time, the schema.sql already includes the Is_Read column. Just run:
```bash
mysql -u root -p unify < src/database/schema.sql
```

**Option B: Existing Database**
If you already have a Message table, run the migration:
```bash
mysql -u root -p unify < src/database/add_is_read_column.sql
```

Or manually execute:
```sql
USE unify;
ALTER TABLE Message ADD COLUMN Is_Read TINYINT(1) DEFAULT 0 AFTER Timestamp;
CREATE INDEX idx_is_read ON Message(Is_Read);
```

### Step 2: Verify File Structure

Ensure these files exist:
- ✅ `src/models/message.py` - Updated with Is_Read field
- ✅ `src/repositories/message.repository.py` - Enhanced with conversation methods
- ✅ `src/controllers/message_controller.py` - Added messaging endpoints
- ✅ `src/templates/messages.html` - Complete messaging UI
- ✅ `src/static/scripts/messages.js` - Frontend logic
- ✅ `src/static/styles/messages.css` - Styling

### Step 3: Test the Application

1. **Start the Flask application:**
   ```bash
   cd src
   python app.py
   ```

2. **Login to UNIFY:**
   - Navigate to http://localhost:5000/login
   - Login with your credentials

3. **Access Messages:**
   - Click on "Messages" in the sidebar
   - You should see the messaging interface

### Step 4: Test Messaging

1. **Create a test message** (if you have another user):
   - Click the "+" button to start a new conversation
   - Select a recipient
   - Type a message and send

2. **Verify database:**
   ```sql
   USE unify;
   SELECT * FROM Message ORDER BY Timestamp DESC LIMIT 5;
   ```

## Common Issues & Solutions

### Issue: "Table 'Message' doesn't exist"
**Solution:** Run the schema.sql to create tables
```bash
mysql -u root -p unify < src/database/schema.sql
```

### Issue: "Column 'Is_Read' doesn't exist"
**Solution:** Run the migration script
```bash
mysql -u root -p unify < src/database/add_is_read_column.sql
```

### Issue: Messages page shows 401 Unauthorized
**Solution:** User is not logged in. Ensure:
1. User has logged in successfully
2. Session is active
3. Check session configuration in app.py

### Issue: CSS not loading
**Solution:** 
1. Clear browser cache (Ctrl+Shift+R)
2. Verify messages.css exists in src/static/styles/
3. Check Flask static folder configuration

### Issue: Messages not refreshing
**Solution:**
1. Check browser console for JavaScript errors
2. Ensure messages.js is loaded
3. Verify API endpoints are accessible

## Testing Checklist

- [ ] Database migration completed successfully
- [ ] Messages page loads without errors
- [ ] Can view conversations list
- [ ] Can click on a conversation
- [ ] Can send a message
- [ ] Can start a new conversation
- [ ] Unread count displays correctly
- [ ] Search works in conversations
- [ ] Messages auto-refresh every 5 seconds
- [ ] Responsive design works on mobile

## Quick Test with Sample Data

```sql
USE unify;

-- Ensure you have at least 2 users
-- Insert test message
INSERT INTO Message (Sender_ID, Receiver_ID, Message_Text, Timestamp, Is_Read)
VALUES (1, 2, 'Hello! This is a test message.', NOW(), 0);

-- Verify
SELECT 
    m.*,
    u1.Username as Sender,
    u2.Username as Receiver
FROM Message m
JOIN User u1 ON m.Sender_ID = u1.User_ID
JOIN User u2 ON m.Receiver_ID = u2.User_ID
ORDER BY m.Timestamp DESC
LIMIT 5;
```

## Next Steps

1. **Read the full documentation:** `docs/MESSAGING_FEATURE.md`
2. **Customize styling** in `src/static/styles/messages.css`
3. **Adjust polling interval** in `src/static/scripts/messages.js` (line ~270)
4. **Add more features** as needed

## Need Help?

- Check server logs for errors
- Review browser console for JavaScript errors
- Verify MySQL connection
- Ensure all dependencies are installed

---

**Setup Complete!** 🎉

Your messaging feature is now ready to use. Users can communicate securely within the UNIFY platform.
