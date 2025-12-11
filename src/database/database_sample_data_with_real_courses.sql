-- ============================================================
-- SQL SERVER Sample Data with REAL COURSES from Schedule 2025
-- This uses actual course codes from your Excel file
-- ============================================================

USE unify;
GO

PRINT '============================================================';
PRINT 'UNIFY DATABASE - Sample Data Setup';
PRINT 'Using REAL course codes from Schedule 2025';
PRINT '============================================================';

-- ============================================================
-- STEP 1: Clear existing data (in correct order)
-- ============================================================
PRINT 'Cleaning up existing data...';

DELETE FROM Reminder;
DELETE FROM Calendar;
DELETE FROM Task;
DELETE FROM Note;
DELETE FROM Schedule;
DELETE FROM Focus_Session;
DELETE FROM Transcript;
DELETE FROM Enrollment;
DELETE FROM Teaching_Assistant;
DELETE FROM Course;
DELETE FROM Message;
DELETE FROM Instructor;
DELETE FROM Student;
DELETE FROM [User];

PRINT 'Cleanup complete!';
GO

-- ============================================================
-- STEP 2: Insert Users
-- ============================================================
PRINT 'Inserting Users...';

-- Password for ALL users is: password123
-- SHA256 hash of "password123" = ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f
INSERT INTO [User] (Username, Email, Password_Hash)
VALUES
('ahmed_hasan', 'ahmed.hasan@student.zewailcity.edu.eg', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'),
('sara_mohamed', 'sara.mohamed@student.zewailcity.edu.eg', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'),
('mohamed_ali', 'mohamed.ali@student.zewailcity.edu.eg', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'),
('dr_khalid_instructor', 'khalid.ahmed@zewailcity.edu.eg', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'),
('dr_nour_instructor', 'nour.mohamed@zewailcity.edu.eg', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'),
('dr_amr_instructor', 'amr.sayed@zewailcity.edu.eg', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f');

PRINT 'Users created successfully';
GO

-- ============================================================
-- STEP 3: Insert Students
-- ============================================================
PRINT 'Inserting Students...';

DECLARE @user1 INT = (SELECT User_ID FROM [User] WHERE Username = 'ahmed_hasan');
DECLARE @user2 INT = (SELECT User_ID FROM [User] WHERE Username = 'sara_mohamed');
DECLARE @user3 INT = (SELECT User_ID FROM [User] WHERE Username = 'mohamed_ali');

INSERT INTO Student (User_ID, Department, Year_Level, GPA)
VALUES
(@user1, 'Computer Science & AI', 3, 3.75),
(@user2, 'Data Science & AI', 2, 3.90),
(@user3, 'Information Technology', 4, 3.65);

PRINT 'Students created successfully';
GO

-- ============================================================
-- STEP 4: Insert Instructors
-- ============================================================
PRINT 'Inserting Instructors...';

DECLARE @user4 INT = (SELECT User_ID FROM [User] WHERE Username = 'dr_khalid_instructor');
DECLARE @user5 INT = (SELECT User_ID FROM [User] WHERE Username = 'dr_nour_instructor');
DECLARE @user6 INT = (SELECT User_ID FROM [User] WHERE Username = 'dr_amr_instructor');

INSERT INTO Instructor (User_ID, Department, Office, Email)
VALUES
(@user4, 'Computer Science & AI', 'Building A - 305', 'khalid.ahmed@zewailcity.edu.eg'),
(@user5, 'Data Science & AI', 'Building B - 201', 'nour.mohamed@zewailcity.edu.eg'),
(@user6, 'Information Technology', 'Building C - 150', 'amr.sayed@zewailcity.edu.eg');

PRINT 'Instructors created successfully';
GO

-- ============================================================
-- STEP 5: Insert REAL Courses from Schedule 2025
-- ============================================================
PRINT 'Inserting REAL courses from Schedule 2025...';

DECLARE @inst1 INT = (SELECT TOP 1 Instructor_ID FROM Instructor ORDER BY Instructor_ID);
DECLARE @inst2 INT = (SELECT Instructor_ID FROM Instructor ORDER BY Instructor_ID OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY);
DECLARE @inst3 INT = (SELECT Instructor_ID FROM Instructor ORDER BY Instructor_ID OFFSET 2 ROWS FETCH NEXT 1 ROWS ONLY);

-- Computer Science & AI Courses
INSERT INTO Course (Course_Name, Credits, Instructor_ID, Schedule)
VALUES
('CSAI 100', 3, @inst1, 'Introduction to Computer Science'),
('CSAI 101', 3, @inst1, 'Programming Fundamentals'),
('CSAI 102', 3, @inst1, 'Data Structures & Algorithms'),
('CSAI 151', 4, @inst1, 'Discrete Mathematics'),
('CSAI 201', 3, @inst1, 'Object-Oriented Programming'),
('CSAI 204', 3, @inst1, 'Database Systems'),
('CSAI 251', 4, @inst1, 'Computer Architecture'),
('CSAI 253', 3, @inst1, 'Operating Systems'),
('CSAI 302', 4, @inst1, 'Software Engineering'),
('CSAI 351', 3, @inst1, 'Artificial Intelligence'),

-- Data Science & AI Courses
('DSAI 103', 3, @inst2, 'Introduction to Data Science'),
('DSAI 104', 3, @inst2, 'Statistical Methods'),
('DSAI 201', 4, @inst2, 'Machine Learning'),
('DSAI 202', 3, @inst2, 'Data Mining'),
('DSAI 305', 4, @inst2, 'Deep Learning'),
('DSAI 308', 3, @inst2, 'Natural Language Processing'),
('DSAI 325', 3, @inst2, 'Computer Vision'),
('DSAI 352', 4, @inst2, 'Big Data Analytics'),
('DSAI 353', 3, @inst2, 'Neural Networks'),

-- Information Technology Courses
('IT 101', 3, @inst3, 'IT Fundamentals'),
('IT 102', 3, @inst3, 'Web Development'),
('IT 103', 3, @inst3, 'Network Fundamentals'),
('IT 206', 4, @inst3, 'Cybersecurity'),
('IT 220', 3, @inst3, 'Cloud Computing'),
('IT 222', 3, @inst3, 'Mobile App Development'),
('IT 309', 4, @inst3, 'Information Systems'),
('IT 310', 3, @inst3, 'DevOps & CI/CD'),
('IT 402', 3, @inst3, 'IT Project Management'),

-- Mathematics Courses
('MATH 101', 4, @inst1, 'Calculus I'),
('MATH 102', 4, @inst1, 'Calculus II'),
('MATH 104', 3, @inst1, 'Linear Algebra'),
('MATH 105', 3, @inst1, 'Differential Equations'),
('MATH 201', 4, @inst2, 'Multivariable Calculus'),
('MATH 202', 3, @inst2, 'Probability & Statistics'),
('MATH 203', 3, @inst2, 'Numerical Analysis'),
('MATH 205', 4, @inst2, 'Abstract Algebra'),

-- Engineering Courses
('ENGR 105', 3, @inst3, 'Engineering Design'),
('ENGR 201', 4, @inst3, 'Engineering Mechanics'),
('ENGR 218', 3, @inst3, 'Electronics'),

-- Physics Courses
('PHYS 101', 4, @inst1, 'Physics I - Mechanics'),
('PHYS 102', 4, @inst1, 'Physics II - E&M'),
('PHYS 103', 3, @inst1, 'Modern Physics'),

-- English Courses
('ENGL 002', 3, @inst2, 'Academic English I'),
('ENGL 003', 3, @inst2, 'Academic English II'),
('ENGL 152', 3, @inst2, 'Technical Writing');

PRINT 'Courses created successfully';
GO

-- ============================================================
-- STEP 6: Insert Enrollments with REALISTIC Grades
-- ============================================================
PRINT 'Inserting Enrollments with grades and semesters...';

DECLARE @stud1 INT = (SELECT TOP 1 Student_ID FROM Student ORDER BY Student_ID);
DECLARE @stud2 INT = (SELECT Student_ID FROM Student ORDER BY Student_ID OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY);
DECLARE @stud3 INT = (SELECT Student_ID FROM Student ORDER BY Student_ID OFFSET 2 ROWS FETCH NEXT 1 ROWS ONLY);

-- Get Course IDs
DECLARE @csai100 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'CSAI 100');
DECLARE @csai101 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'CSAI 101');
DECLARE @csai102 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'CSAI 102');
DECLARE @csai151 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'CSAI 151');
DECLARE @csai201 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'CSAI 204');
DECLARE @csai302 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'CSAI 302');
DECLARE @dsai103 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'DSAI 103');
DECLARE @dsai201 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'DSAI 201');
DECLARE @dsai305 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'DSAI 305');
DECLARE @math101 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'MATH 101');
DECLARE @math102 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'MATH 102');
DECLARE @math104 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'MATH 104');
DECLARE @phys101 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'PHYS 101');
DECLARE @engl002 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'ENGL 002');
DECLARE @it101 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'IT 101');
DECLARE @it102 INT = (SELECT Course_ID FROM Course WHERE Course_Name = 'IT 102');

-- Student 1 (Ahmed) - Year 3 CSAI Student
-- Fall 2023 (First year)
INSERT INTO Enrollment (Student_ID, Course_ID, Status, Grade, Semester)
VALUES
(@stud1, @csai100, 'completed', 'A', 'Fall 2023'),
(@stud1, @csai101, 'completed', 'A-', 'Fall 2023'),
(@stud1, @math101, 'completed', 'B+', 'Fall 2023'),
(@stud1, @phys101, 'completed', 'A', 'Fall 2023'),
(@stud1, @engl002, 'completed', 'B+', 'Fall 2023');

-- Spring 2024
INSERT INTO Enrollment (Student_ID, Course_ID, Status, Grade, Semester)
VALUES
(@stud1, @csai102, 'completed', 'A', 'Spring 2024'),
(@stud1, @csai151, 'completed', 'A', 'Spring 2024'),
(@stud1, @math102, 'completed', 'A-', 'Spring 2024'),
(@stud1, @dsai103, 'completed', 'A', 'Spring 2024');

-- Fall 2024 (Second year)
INSERT INTO Enrollment (Student_ID, Course_ID, Status, Grade, Semester)
VALUES
(@stud1, @csai201, 'completed', 'A', 'Fall 2024'),
(@stud1, @dsai201, 'completed', 'A-', 'Fall 2024'),
(@stud1, @math104, 'completed', 'B+', 'Fall 2024');

-- Student 2 (Sara) - Year 2 DSAI Student  
-- Fall 2023
INSERT INTO Enrollment (Student_ID, Course_ID, Status, Grade, Semester)
VALUES
(@stud2, @csai100, 'completed', 'A', 'Fall 2023'),
(@stud2, @dsai103, 'completed', 'A', 'Fall 2023'),
(@stud2, @math101, 'completed', 'A', 'Fall 2023'),
(@stud2, @engl002, 'completed', 'A-', 'Fall 2023');

-- Spring 2024
INSERT INTO Enrollment (Student_ID, Course_ID, Status, Grade, Semester)
VALUES
(@stud2, @csai101, 'completed', 'A', 'Spring 2024'),
(@stud2, @dsai201, 'completed', 'A', 'Spring 2024'),
(@stud2, @math102, 'completed', 'A-', 'Spring 2024');

-- Fall 2024
INSERT INTO Enrollment (Student_ID, Course_ID, Status, Grade, Semester)
VALUES
(@stud2, @csai102, 'completed', 'A', 'Fall 2024'),
(@stud2, @dsai305, 'completed', 'A', 'Fall 2024'),
(@stud2, @math104, 'completed', 'A', 'Fall 2024');

-- Student 3 (Mohamed) - Year 4 IT Student
-- Fall 2023
INSERT INTO Enrollment (Student_ID, Course_ID, Status, Grade, Semester)
VALUES
(@stud3, @it101, 'completed', 'B+', 'Fall 2023'),
(@stud3, @it102, 'completed', 'A-', 'Fall 2023'),
(@stud3, @math101, 'completed', 'B', 'Fall 2023');

-- Spring 2024
INSERT INTO Enrollment (Student_ID, Course_ID, Status, Grade, Semester)
VALUES
(@stud3, @csai101, 'completed', 'B+', 'Spring 2024'),
(@stud3, @dsai103, 'completed', 'A-', 'Spring 2024');

PRINT 'Enrollments created successfully';
GO

-- ============================================================
-- STEP 7: Insert Tasks
-- ============================================================
PRINT 'Inserting sample tasks...';

DECLARE @stud1 INT = (SELECT TOP 1 Student_ID FROM Student ORDER BY Student_ID);
DECLARE @stud2 INT = (SELECT Student_ID FROM Student ORDER BY Student_ID OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY);

INSERT INTO Task (Student_ID, Task_Title, Due_Date, Priority, Status)
VALUES
(@stud1, 'CSAI 302 - Project Proposal', '2025-12-20 23:59:00', 'high', 'pending'),
(@stud1, 'DSAI 305 - Neural Network Assignment', '2025-12-25 23:59:00', 'high', 'pending'),
(@stud1, 'MATH 202 - Probability Problem Set', '2025-12-18 14:00:00', 'medium', 'completed'),
(@stud2, 'DSAI 201 - ML Midterm Prep', '2025-12-22 10:00:00', 'high', 'pending'),
(@stud2, 'CSAI 102 - Algorithm Analysis', '2025-12-19 23:59:00', 'medium', 'pending');

PRINT 'Tasks created successfully';
GO

-- ============================================================
-- VERIFICATION
-- ============================================================
PRINT '';
PRINT '============================================================';
PRINT 'VERIFICATION: Data Summary';
PRINT '============================================================';

PRINT '';
PRINT 'Users Created:';
SELECT User_ID, Username, Email FROM [User];

PRINT '';
PRINT 'Students:';
SELECT s.Student_ID, u.Username, s.Department, s.Year_Level, s.GPA
FROM Student s
JOIN [User] u ON s.User_ID = u.User_ID;

PRINT '';
PRINT 'Instructors:';
SELECT i.Instructor_ID, u.Username as Name, i.Department
FROM Instructor i
JOIN [User] u ON i.User_ID = u.User_ID;

PRINT '';
PRINT 'Courses (showing first 20):';
SELECT TOP 20 Course_ID, Course_Name, Credits FROM Course ORDER BY Course_Name;

PRINT '';
PRINT 'Enrollments with Grades:';
SELECT 
    u.Username as Student,
    c.Course_Name,
    e.Grade,
    e.Semester,
    e.Status
FROM Enrollment e
JOIN Student s ON e.Student_ID = s.Student_ID
JOIN [User] u ON s.User_ID = u.User_ID
JOIN Course c ON e.Course_ID = c.Course_ID
ORDER BY u.Username, e.Semester, c.Course_Name;

PRINT '';
PRINT '============================================================';
PRINT 'Setup Complete!';
PRINT '';
PRINT '*** LOGIN CREDENTIALS ***';
PRINT 'Password for ALL users: password123';
PRINT '';
PRINT 'Student Accounts:';
PRINT '  Email: ahmed.hasan@student.zewailcity.edu.eg';
PRINT '  Email: sara.mohamed@student.zewailcity.edu.eg';
PRINT '  Email: mohamed.ali@student.zewailcity.edu.eg';
PRINT '';
PRINT 'Instructor Accounts:';
PRINT '  Email: khalid.ahmed@zewailcity.edu.eg';
PRINT '  Email: nour.mohamed@zewailcity.edu.eg';
PRINT '  Email: amr.sayed@zewailcity.edu.eg';
PRINT '';
PRINT 'Next Steps:';
PRINT '1. Start your Flask app: cd UNIFY/src && python app.py';
PRINT '2. Navigate to: http://localhost:5000/login';
PRINT '3. Login with any email above using password: password123';
PRINT '4. Go to Transcript page to view real course data!';
PRINT '============================================================';
GO

