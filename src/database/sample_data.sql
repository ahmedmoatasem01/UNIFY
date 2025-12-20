-- =============================================
-- SAMPLE DATA FOR UNIFY DATABASE
-- SQL Server Syntax
-- =============================================
-- This script inserts sample data for testing
-- Run this after creating all tables
-- =============================================

USE unify;
GO

-- Clear existing data (optional - comment out if you want to keep existing data)
-- DELETE FROM Reminder;
-- DELETE FROM Calendar;
-- DELETE FROM CourseMaterial;
-- DELETE FROM Enrollment;
-- DELETE FROM Task;
-- DELETE FROM Message;
-- DELETE FROM Course_Schedule_Slot;
-- DELETE FROM Course;
-- DELETE FROM Student;
-- DELETE FROM Instructor;
-- DELETE FROM [User];
-- GO

-- =============================================
-- INSERT USERS
-- =============================================
SET IDENTITY_INSERT [User] ON;
GO

INSERT INTO [User] (User_ID, Username, Email, Password_Hash, Created_At) VALUES
(1, 'john_doe', 'john.doe@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', GETDATE()),
(2, 'jane_smith', 'jane.smith@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', GETDATE()),
(3, 'prof_brown', 'prof.brown@university.edu', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', GETDATE()),
(4, 'prof_wilson', 'prof.wilson@university.edu', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', GETDATE()),
(5, 'alice_student', 'alice@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', GETDATE()),
(6, 'bob_student', 'bob@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', GETDATE());
-- Password hash above is for "password123"

SET IDENTITY_INSERT [User] OFF;
GO

-- =============================================
-- INSERT STUDENTS
-- =============================================
SET IDENTITY_INSERT Student ON;
GO

INSERT INTO Student (Student_ID, User_ID, Department, Year_Level, GPA) VALUES
(1, 1, 'Computer Science', 2, 3.5),
(2, 2, 'Computer Science', 3, 3.8),
(5, 5, 'Computer Science', 1, 3.2),
(6, 6, 'Engineering', 2, 3.6);
-- Note: Using IDs 1,2,5,6 to match User_IDs above

SET IDENTITY_INSERT Student OFF;
GO

-- =============================================
-- INSERT INSTRUCTORS
-- =============================================
SET IDENTITY_INSERT Instructor ON;
GO

INSERT INTO Instructor (Instructor_ID, User_ID, Department, Office, Email) VALUES
(1, 3, 'Computer Science', 'Building A, Room 201', 'prof.brown@university.edu'),
(2, 4, 'Computer Science', 'Building A, Room 205', 'prof.wilson@university.edu');

SET IDENTITY_INSERT Instructor OFF;
GO

-- =============================================
-- INSERT COURSES
-- =============================================
SET IDENTITY_INSERT Course ON;
GO

INSERT INTO Course (Course_ID, Course_Name, Credits, Instructor_ID, Schedule) VALUES
(1, 'Introduction to Programming', 3, 1, 'Monday, Wednesday 10:00 AM - 11:30 AM'),
(2, 'Data Structures and Algorithms', 4, 1, 'Tuesday, Thursday 2:00 PM - 4:00 PM'),
(3, 'Database Systems', 3, 2, 'Monday, Wednesday 1:00 PM - 2:30 PM'),
(4, 'Web Development', 3, 2, 'Tuesday, Thursday 9:00 AM - 10:30 AM'),
(5, 'Machine Learning', 4, 1, 'Monday, Wednesday 3:00 PM - 5:00 PM');

SET IDENTITY_INSERT Course OFF;
GO

-- =============================================
-- INSERT ENROLLMENTS
-- =============================================
SET IDENTITY_INSERT Enrollment ON;
GO

INSERT INTO Enrollment (Enrollment_ID, Student_ID, Course_ID, Status, Grade, Semester) VALUES
(1, 1, 1, 'enrolled', NULL, 'Spring 2024'),
(2, 1, 2, 'enrolled', NULL, 'Spring 2024'),
(3, 1, 3, 'completed', 'A', 'Fall 2023'),
(4, 2, 2, 'enrolled', NULL, 'Spring 2024'),
(5, 2, 3, 'enrolled', NULL, 'Spring 2024'),
(6, 2, 4, 'completed', 'B+', 'Fall 2023'),
(7, 5, 1, 'enrolled', NULL, 'Spring 2024'),
(8, 6, 2, 'enrolled', NULL, 'Spring 2024');

SET IDENTITY_INSERT Enrollment OFF;
GO

-- =============================================
-- INSERT COURSE SCHEDULE SLOTS
-- =============================================
SET IDENTITY_INSERT Course_Schedule_Slot ON;
GO

INSERT INTO Course_Schedule_Slot (Slot_ID, Course_ID, Course_Code, Section, Day, Start_Time, End_Time, Slot_Type, Sub_Type, Academic_Year, Term) VALUES
-- Course 1: Introduction to Programming
(1, 1, 'CS 101', 1, 'Monday', '10:00', '11:30', 'lecture', 'LCTR', 2024, 'SPRING'),
(2, 1, 'CS 101', 1, 'Wednesday', '10:00', '11:30', 'lecture', 'LCTR', 2024, 'SPRING'),
(3, 1, 'CS 101', 1, 'Friday', '10:00', '11:30', 'lab', 'LAB', 2024, 'SPRING'),

-- Course 2: Data Structures and Algorithms
(4, 2, 'CS 201', 1, 'Tuesday', '14:00', '16:00', 'lecture', 'LCTR', 2024, 'SPRING'),
(5, 2, 'CS 201', 1, 'Thursday', '14:00', '16:00', 'lecture', 'LCTR', 2024, 'SPRING'),
(6, 2, 'CS 201', 1, 'Saturday', '10:00', '12:00', 'lab', 'LAB', 2024, 'SPRING'),

-- Course 3: Database Systems
(7, 3, 'CS 301', 1, 'Monday', '13:00', '14:30', 'lecture', 'LCTR', 2024, 'SPRING'),
(8, 3, 'CS 301', 1, 'Wednesday', '13:00', '14:30', 'lecture', 'LCTR', 2024, 'SPRING'),
(9, 3, 'CS 301', 1, 'Friday', '13:00', '14:30', 'tutorial', 'TUTR', 2024, 'SPRING'),

-- Course 4: Web Development
(10, 4, 'CS 302', 1, 'Tuesday', '09:00', '10:30', 'lecture', 'LCTR', 2024, 'SPRING'),
(11, 4, 'CS 302', 1, 'Thursday', '09:00', '10:30', 'lecture', 'LCTR', 2024, 'SPRING'),

-- Course 5: Machine Learning
(12, 5, 'CS 401', 1, 'Monday', '15:00', '17:00', 'lecture', 'LCTR', 2024, 'SPRING'),
(13, 5, 'CS 401', 1, 'Wednesday', '15:00', '17:00', 'lecture', 'LCTR', 2024, 'SPRING');

SET IDENTITY_INSERT Course_Schedule_Slot OFF;
GO

-- =============================================
-- INSERT TASKS
-- =============================================
SET IDENTITY_INSERT [Task] ON;
GO

INSERT INTO [Task] (Task_ID, Student_ID, Task_Title, Due_Date, Priority, Status) VALUES
(1, 1, 'Complete Programming Assignment 1', DATEADD(day, 7, GETDATE()), 'high', 'pending'),
(2, 1, 'Study for Midterm Exam', DATEADD(day, 14, GETDATE()), 'high', 'pending'),
(3, 1, 'Submit Lab Report', DATEADD(day, 3, GETDATE()), 'medium', 'pending'),
(4, 2, 'Database Project - Phase 1', DATEADD(day, 10, GETDATE()), 'high', 'pending'),
(5, 2, 'Read Chapter 5-7', DATEADD(day, 5, GETDATE()), 'low', 'pending'),
(6, 1, 'Review Algorithms Notes', DATEADD(day, -2, GETDATE()), 'medium', 'completed');

SET IDENTITY_INSERT [Task] OFF;
GO

-- =============================================
-- INSERT MESSAGES
-- =============================================
SET IDENTITY_INSERT [Message] ON;
GO

INSERT INTO [Message] (Message_ID, Sender_ID, Receiver_ID, Message_Text, Timestamp, Is_Read) VALUES
(1, 3, 1, 'Hi John, please submit your assignment by Friday.', DATEADD(hour, -2, GETDATE()), 0),
(2, 1, 3, 'Thank you professor, I will submit it on time.', DATEADD(hour, -1, GETDATE()), 1),
(3, 2, 1, 'Hey John, can you help me with the database assignment?', DATEADD(hour, -5, GETDATE()), 0),
(4, 4, 2, 'Jane, great work on your last project!', DATEADD(day, -1, GETDATE()), 0),
(5, 5, 1, 'Hi, are you attending the study group today?', DATEADD(hour, -3, GETDATE()), 0);

SET IDENTITY_INSERT [Message] OFF;
GO

-- =============================================
-- INSERT CALENDAR EVENTS
-- =============================================
SET IDENTITY_INSERT Calendar ON;
GO

INSERT INTO Calendar (Event_ID, Student_ID, Title, Date, Time, Source) VALUES
(1, 1, 'Programming Midterm Exam', DATEADD(day, 14, CAST(GETDATE() AS DATE)), '10:00', 'Course'),
(2, 1, 'Study Group Meeting', DATEADD(day, 2, CAST(GETDATE() AS DATE)), '18:00', 'Student'),
(3, 2, 'Database Project Presentation', DATEADD(day, 21, CAST(GETDATE() AS DATE)), '14:00', 'Course'),
(4, 1, 'Assignment Due: Lab Report', DATEADD(day, 3, CAST(GETDATE() AS DATE)), '23:59', 'Course'),
(5, 2, 'Algorithms Quiz', DATEADD(day, 7, CAST(GETDATE() AS DATE)), '14:00', 'Course'),
(6, 1, 'Group Project Meeting', DATEADD(day, 5, CAST(GETDATE() AS DATE)), '16:00', 'Student');

SET IDENTITY_INSERT Calendar OFF;
GO

-- =============================================
-- INSERT REMINDERS
-- =============================================
SET IDENTITY_INSERT Reminder ON;
GO

INSERT INTO Reminder (Reminder_ID, Student_ID, Event_ID, Reminder_Time, Status) VALUES
(1, 1, 1, DATEADD(day, 13, GETDATE()), 'pending'),
(2, 1, 2, DATEADD(day, 2, DATEADD(hour, -1, CAST(GETDATE() AS DATETIME))), 'pending'),
(3, 2, 3, DATEADD(day, 20, GETDATE()), 'pending'),
(4, 1, 4, DATEADD(day, 3, DATEADD(hour, -2, CAST(GETDATE() AS DATETIME))), 'pending');

SET IDENTITY_INSERT Reminder OFF;
GO

-- =============================================
-- INSERT TRANSCRIPTS
-- =============================================
SET IDENTITY_INSERT Transcript ON;
GO

INSERT INTO Transcript (Transcript_ID, Student_ID, GPA, PDF_Path, Issue_Date) VALUES
(1, 1, 3.5, '/transcripts/student1_transcript_2024.pdf', DATEADD(month, -2, GETDATE())),
(2, 2, 3.8, '/transcripts/student2_transcript_2024.pdf', DATEADD(month, -2, GETDATE()));

SET IDENTITY_INSERT Transcript OFF;
GO

-- =============================================
-- INSERT SCHEDULES (Optimized schedules for students)
-- =============================================
SET IDENTITY_INSERT [Schedule] ON;
GO

-- Sample optimized schedule for student 1
DECLARE @schedule_json1 NVARCHAR(MAX) = '[{"course_code":"CS 101","section":1,"day":"Monday","start":"10:00","end":"11:30","type":"lecture"},{"course_code":"CS 101","section":1,"day":"Wednesday","start":"10:00","end":"11:30","type":"lecture"},{"course_code":"CS 201","section":1,"day":"Tuesday","start":"14:00","end":"16:00","type":"lecture"}]';

INSERT INTO [Schedule] (Schedule_ID, Student_ID, Course_List, Optimized) VALUES
(1, 1, @schedule_json1, 1),
(2, 2, '[{"course_code":"CS 201","section":1,"day":"Tuesday","start":"14:00","end":"16:00","type":"lecture"}]', 1);

SET IDENTITY_INSERT [Schedule] OFF;
GO

-- =============================================
-- INSERT USER SETTINGS (for existing users)
-- =============================================
INSERT INTO [User_Settings] (User_ID, email_notifications, push_notifications, calendar_reminders, assignment_deadlines, theme, language)
SELECT User_ID, 1, 1, 1, 1, 'dark', 'en'
FROM [User]
WHERE User_ID NOT IN (SELECT User_ID FROM User_Settings);
GO

PRINT '';
PRINT '========================================';
PRINT 'SAMPLE DATA INSERTED SUCCESSFULLY!';
PRINT '========================================';
PRINT '';
PRINT 'Summary:';
PRINT '  - Users: 6';
PRINT '  - Students: 4';
PRINT '  - Instructors: 2';
PRINT '  - Courses: 5';
PRINT '  - Enrollments: 8';
PRINT '  - Schedule Slots: 13';
PRINT '  - Tasks: 6';
PRINT '  - Messages: 5';
PRINT '  - Calendar Events: 6';
PRINT '  - Reminders: 4';
PRINT '  - Transcripts: 2';
PRINT '  - Schedules: 2';
PRINT '';
PRINT 'You can now test the application with this sample data.';
PRINT 'Default password for all users: password123';
PRINT '========================================';
GO

