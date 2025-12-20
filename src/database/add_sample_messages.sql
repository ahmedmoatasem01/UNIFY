-- Add Sample Messages for Testing
-- Run this AFTER verifying Message table exists

USE unify;
GO

PRINT '============================================================';
PRINT 'Adding Sample Messages';
PRINT '============================================================';

-- Insert sample messages between students and instructors
-- Using existing users from the database

DECLARE @student1_id INT, @student2_id INT, @student3_id INT;
DECLARE @instructor1_id INT, @instructor2_id INT, @instructor3_id INT;

-- Get User IDs
SELECT @student1_id = User_ID FROM [User] WHERE Email = 'ahmed.hasan@student.zewailcity.edu.eg';
SELECT @student2_id = User_ID FROM [User] WHERE Email = 'sara.mohamed@student.zewailcity.edu.eg';
SELECT @student3_id = User_ID FROM [User] WHERE Email = 'mohamed.ali@student.zewailcity.edu.eg';
SELECT @instructor1_id = User_ID FROM [User] WHERE Email = 'khalid.ahmed@zewailcity.edu.eg';
SELECT @instructor2_id = User_ID FROM [User] WHERE Email = 'nour.mohamed@zewailcity.edu.eg';
SELECT @instructor3_id = User_ID FROM [User] WHERE Email = 'amr.sayed@zewailcity.edu.eg';

-- Check if users exist
IF @student1_id IS NULL OR @instructor1_id IS NULL
BEGIN
    PRINT '❌ ERROR: Required users not found in database!';
    PRINT 'Please run the sample data script first: database_sample_data_with_real_courses.sql';
    RETURN;
END

PRINT '✅ Users found. Adding messages...';
PRINT '';

-- Conversation 1: Student 1 with Instructor 1
INSERT INTO [Message] (Sender_ID, Receiver_ID, Message_Text, Timestamp, Is_Read)
VALUES 
    (@instructor1_id, @student1_id, 'Hello Ahmed, welcome to CSAI 101. Please check the course materials.', DATEADD(day, -2, GETDATE()), 1),
    (@student1_id, @instructor1_id, 'Thank you Dr. Khalid! I have a question about the assignment.', DATEADD(day, -2, DATEADD(hour, 1, GETDATE())), 1),
    (@instructor1_id, @student1_id, 'Sure, what would you like to know?', DATEADD(day, -2, DATEADD(hour, 2, GETDATE())), 1),
    (@student1_id, @instructor1_id, 'When is the deadline for the first project?', DATEADD(day, -1, GETDATE()), 0);

-- Conversation 2: Student 1 with Student 2
INSERT INTO [Message] (Sender_ID, Receiver_ID, Message_Text, Timestamp, Is_Read)
VALUES 
    (@student2_id, @student1_id, 'Hey Ahmed! Are you free to study together?', DATEADD(hour, -5, GETDATE()), 0),
    (@student2_id, @student1_id, 'We can go over the Data Structures chapter.', DATEADD(hour, -4, GETDATE()), 0);

-- Conversation 3: Student 1 with Instructor 2
INSERT INTO [Message] (Sender_ID, Receiver_ID, Message_Text, Timestamp, Is_Read)
VALUES 
    (@student1_id, @instructor2_id, 'Good morning Dr. Nour, I missed today''s lecture. Can I get the notes?', DATEADD(hour, -10, GETDATE()), 1),
    (@instructor2_id, @student1_id, 'Good morning Ahmed. The notes are uploaded to the portal.', DATEADD(hour, -9, GETDATE()), 1);

-- Conversation 4: Student 2 with Instructor 1
INSERT INTO [Message] (Sender_ID, Receiver_ID, Message_Text, Timestamp, Is_Read)
VALUES 
    (@student2_id, @instructor1_id, 'Dr. Khalid, can I submit my assignment one day late?', DATEADD(day, -1, GETDATE()), 1),
    (@instructor1_id, @student2_id, 'Yes Sara, but please email me the reason.', DATEADD(day, -1, DATEADD(hour, 2, GETDATE())), 1);

PRINT '';
PRINT '✅ Sample messages added successfully!';
PRINT '';
PRINT 'Message Summary:';
SELECT COUNT(*) as Total_Messages FROM [Message];

PRINT '';
PRINT 'Conversations for ahmed_hasan:';
SELECT 
    u.Username as Other_User,
    COUNT(*) as Message_Count,
    MAX(m.Timestamp) as Last_Message_Time
FROM [Message] m
JOIN [User] u ON (CASE WHEN m.Sender_ID = @student1_id THEN m.Receiver_ID ELSE m.Sender_ID END) = u.User_ID
WHERE m.Sender_ID = @student1_id OR m.Receiver_ID = @student1_id
GROUP BY u.Username
ORDER BY Last_Message_Time DESC;

PRINT '';
PRINT '============================================================';
PRINT 'Now refresh http://localhost:5000/messages to see conversations!';
PRINT '============================================================';

GO

