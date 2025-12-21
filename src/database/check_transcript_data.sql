-- ============================================================
-- Check Transcript Data - Debugging Script
-- Run this to see what data exists for the logged-in user
-- ============================================================

USE unify;
GO

PRINT '============================================================';
PRINT 'Checking Transcript Data for ahmed_hasan';
PRINT '============================================================';
PRINT '';

-- Check User
PRINT '1. USER INFO:';
SELECT User_ID, Username, Email 
FROM [User] 
WHERE Email = 'ahmed.hasan@student.zewailcity.edu.eg';

PRINT '';
PRINT '2. STUDENT INFO:';
SELECT s.Student_ID, s.User_ID, u.Username, s.Department, s.Year_Level, s.GPA
FROM Student s
JOIN [User] u ON s.User_ID = u.User_ID
WHERE u.Email = 'ahmed.hasan@student.zewailcity.edu.eg';

PRINT '';
PRINT '3. ENROLLMENTS WITH GRADES:';
SELECT 
    e.Enrollment_ID,
    e.Student_ID,
    c.Course_Name,
    e.Grade,
    e.Semester,
    e.Status,
    c.Credits
FROM Enrollment e
JOIN Course c ON e.Course_ID = c.Course_ID
JOIN Student s ON e.Student_ID = s.Student_ID
JOIN [User] u ON s.User_ID = u.User_ID
WHERE u.Email = 'ahmed.hasan@student.zewailcity.edu.eg'
ORDER BY e.Semester, c.Course_Name;

PRINT '';
PRINT '4. TOTAL ENROLLMENTS FOR ALL STUDENTS:';
SELECT 
    u.Username,
    COUNT(e.Enrollment_ID) as Total_Enrollments,
    COUNT(CASE WHEN e.Grade IS NOT NULL THEN 1 END) as With_Grades,
    COUNT(CASE WHEN e.Semester IS NOT NULL THEN 1 END) as With_Semesters
FROM [User] u
JOIN Student s ON u.User_ID = s.User_ID
LEFT JOIN Enrollment e ON s.Student_ID = e.Student_ID
GROUP BY u.Username, u.User_ID
ORDER BY u.Username;

PRINT '';
PRINT '============================================================';
PRINT 'If you see 0 enrollments for ahmed_hasan, the data was not inserted!';
PRINT '============================================================';
GO

