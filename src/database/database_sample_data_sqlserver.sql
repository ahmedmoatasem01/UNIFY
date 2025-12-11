-- ============================================================
-- SQL SERVER Sample Data Script for Unify Database
-- Run this entire script in SSMS after creating your tables
-- ============================================================

USE unify;
GO

-- ============================================================
-- STEP 1: Insert Users
-- ============================================================
PRINT 'Inserting Users...';

-- Check if users already exist
IF NOT EXISTS (SELECT 1 FROM [User] WHERE Username = 'ahmed_student')
BEGIN
    INSERT INTO [User] (Username, Email, Password_Hash)
    VALUES
    ('ahmed_student', 'ahmed@student.unify.edu', 'hashed_password_1'),
    ('sara_student', 'sara@student.unify.edu', 'hashed_password_2'),
    ('mohamed_student', 'mohamed@student.unify.edu', 'hashed_password_3'),
    ('dr_khalid', 'khalid@instructor.unify.edu', 'hashed_password_4'),
    ('dr_nour', 'nour@instructor.unify.edu', 'hashed_password_5');
    
    PRINT 'Users inserted successfully.';
END
ELSE
BEGIN
    PRINT 'Users already exist, skipping...';
END
GO

-- ============================================================
-- STEP 2: Insert Students
-- ============================================================
PRINT 'Inserting Students...';

-- Get User IDs
DECLARE @user1 INT = (SELECT User_ID FROM [User] WHERE Username = 'ahmed_student');
DECLARE @user2 INT = (SELECT User_ID FROM [User] WHERE Username = 'sara_student');
DECLARE @user3 INT = (SELECT User_ID FROM [User] WHERE Username = 'mohamed_student');

-- Insert Students if they don't exist
IF NOT EXISTS (SELECT 1 FROM Student WHERE User_ID = @user1)
BEGIN
    INSERT INTO Student (User_ID, Department, Year_Level, GPA)
    VALUES
    (@user1, 'Computer Science', 3, 3.75),
    (@user2, 'Data Science', 2, 3.90),
    (@user3, 'Artificial Intelligence', 4, 3.65);
    
    PRINT 'Students inserted successfully.';
END
ELSE
BEGIN
    PRINT 'Students already exist, skipping...';
END
GO

-- ============================================================
-- STEP 3: Insert Instructors
-- ============================================================
PRINT 'Inserting Instructors...';

DECLARE @user4 INT = (SELECT User_ID FROM [User] WHERE Username = 'dr_khalid');
DECLARE @user5 INT = (SELECT User_ID FROM [User] WHERE Username = 'dr_nour');

IF NOT EXISTS (SELECT 1 FROM Instructor WHERE User_ID = @user4)
BEGIN
    INSERT INTO Instructor (User_ID, Department, Office, Email)
    VALUES
    (@user4, 'Computer Science', 'Building A - 305', 'khalid@instructor.unify.edu'),
    (@user5, 'Data Science', 'Building B - 201', 'nour@instructor.unify.edu');
    
    PRINT 'Instructors inserted successfully.';
END
ELSE
BEGIN
    PRINT 'Instructors already exist, skipping...';
END
GO

-- ============================================================
-- STEP 4: Insert Courses
-- ============================================================
PRINT 'Inserting Courses...';

-- Get Instructor IDs
DECLARE @inst1 INT = (SELECT TOP 1 Instructor_ID FROM Instructor ORDER BY Instructor_ID);
DECLARE @inst2 INT = (SELECT TOP 1 Instructor_ID FROM Instructor ORDER BY Instructor_ID DESC);

IF NOT EXISTS (SELECT 1 FROM Course WHERE Course_Name = 'Introduction to Programming')
BEGIN
    INSERT INTO Course (Course_Name, Credits, Instructor_ID, Schedule)
    VALUES
    ('Introduction to Programming', 3, @inst1, 'Sun-Tue 10:00-12:00'),
    ('Database Systems', 3, @inst1, 'Mon-Wed 14:00-16:00'),
    ('Data Structures', 4, @inst1, 'Tue-Thu 09:00-11:00'),
    ('Machine Learning', 4, @inst2, 'Sun-Wed 12:00-14:00'),
    ('Web Development', 3, @inst2, 'Mon-Thu 16:00-18:00'),
    ('Algorithms', 4, @inst1, 'Sat-Mon 10:00-12:00');
    
    PRINT 'Courses inserted successfully.';
END
ELSE
BEGIN
    PRINT 'Courses already exist, skipping...';
END
GO

-- ============================================================
-- STEP 5: Insert Enrollments with Grades
-- ============================================================
PRINT 'Inserting Enrollments...';

-- Get Student IDs
DECLARE @stud1 INT = (SELECT TOP 1 Student_ID FROM Student ORDER BY Student_ID);
DECLARE @stud2 INT = (SELECT Student_ID FROM Student ORDER BY Student_ID OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY);
DECLARE @stud3 INT = (SELECT Student_ID FROM Student ORDER BY Student_ID OFFSET 2 ROWS FETCH NEXT 1 ROWS ONLY);

-- Get Course IDs
DECLARE @course1 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'Introduction to Programming');
DECLARE @course2 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'Database Systems');
DECLARE @course3 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'Data Structures');
DECLARE @course4 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'Machine Learning');
DECLARE @course5 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'Web Development');
DECLARE @course6 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'Algorithms');

-- Delete existing enrollments to avoid duplicates (optional)
DELETE FROM Enrollment WHERE Student_ID IN (@stud1, @stud2, @stud3);

-- Insert enrollments with grades and semesters
INSERT INTO Enrollment (Student_ID, Course_ID, Status, Grade, Semester)
VALUES
-- Student 1 - Fall 2023
(@stud1, @course1, 'completed', 'A', 'Fall 2023'),
(@stud1, @course2, 'completed', 'A-', 'Fall 2023'),
(@stud1, @course3, 'completed', 'B+', 'Fall 2023'),

-- Student 1 - Spring 2024
(@stud1, @course4, 'completed', 'A', 'Spring 2024'),
(@stud1, @course5, 'completed', 'A', 'Spring 2024'),

-- Student 2 - Fall 2023
(@stud2, @course1, 'completed', 'A', 'Fall 2023'),
(@stud2, @course3, 'completed', 'A', 'Fall 2023'),

-- Student 2 - Spring 2024  
(@stud2, @course2, 'completed', 'A-', 'Spring 2024'),
(@stud2, @course4, 'completed', 'A', 'Spring 2024'),
(@stud2, @course6, 'completed', 'A', 'Spring 2024'),

-- Student 3 - Fall 2023
(@stud3, @course1, 'completed', 'B+', 'Fall 2023'),
(@stud3, @course2, 'completed', 'B', 'Fall 2023'),

-- Student 3 - Spring 2024
(@stud3, @course3, 'completed', 'A-', 'Spring 2024'),
(@stud3, @course5, 'completed', 'B+', 'Spring 2024');

PRINT 'Enrollments inserted successfully.';
GO

-- ============================================================
-- STEP 6: Insert Tasks
-- ============================================================
PRINT 'Inserting Tasks...';

DECLARE @stud1 INT = (SELECT TOP 1 Student_ID FROM Student ORDER BY Student_ID);
DECLARE @stud2 INT = (SELECT Student_ID FROM Student ORDER BY Student_ID OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY);

DELETE FROM Task WHERE Student_ID IN (@stud1, @stud2);

INSERT INTO Task (Student_ID, Task_Title, Due_Date, Priority, Status)
VALUES
(@stud1, 'Complete Programming Assignment 3', '2025-12-25 23:59:00', 'high', 'pending'),
(@stud1, 'Study for Database Midterm', '2025-12-20 14:00:00', 'high', 'pending'),
(@stud2, 'ML Project Proposal', '2025-12-30 23:59:00', 'medium', 'pending'),
(@stud2, 'Read Chapter 5-7', '2025-12-18 23:59:00', 'low', 'completed');

PRINT 'Tasks inserted successfully.';
GO

-- ============================================================
-- VERIFICATION - Check what was inserted
-- ============================================================
PRINT '============================================================';
PRINT 'VERIFICATION: Checking inserted data...';
PRINT '============================================================';

PRINT 'Users:';
SELECT User_ID, Username, Email FROM [User];

PRINT '';
PRINT 'Students:';
SELECT s.Student_ID, u.Username, s.Department, s.Year_Level, s.GPA
FROM Student s
JOIN [User] u ON s.User_ID = u.User_ID;

PRINT '';
PRINT 'Instructors:';
SELECT i.Instructor_ID, u.Username, i.Department, i.Office
FROM Instructor i
JOIN [User] u ON i.User_ID = u.User_ID;

PRINT '';
PRINT 'Courses:';
SELECT Course_ID, Course_Name, Credits, Instructor_ID FROM Course;

PRINT '';
PRINT 'Enrollments with Grades:';
SELECT 
    e.Enrollment_ID,
    s.Student_ID,
    u.Username as Student_Name,
    c.Course_Name,
    e.Status,
    e.Grade,
    e.Semester
FROM Enrollment e
JOIN Student s ON e.Student_ID = s.Student_ID
JOIN [User] u ON s.User_ID = u.User_ID
JOIN Course c ON e.Course_ID = c.Course_ID
ORDER BY s.Student_ID, e.Semester, c.Course_Name;

PRINT '';
PRINT '============================================================';
PRINT 'Setup complete! You can now test the Transcript page.';
PRINT 'Navigate to: http://localhost:5000/transcript';
PRINT '============================================================';

