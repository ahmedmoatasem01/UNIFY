-- ============================================================
-- Test Script: Verify Smart Reminders Saves to Database
-- Run this BEFORE and AFTER adding a reminder on the website
-- ============================================================

USE unify;
GO

PRINT '============================================================';
PRINT 'BEFORE: Current Tasks for ahmed_hasan';
PRINT '============================================================';

SELECT 
    t.Task_ID,
    t.Task_Title,
    t.Due_Date,
    t.Priority,
    t.Status,
    s.Student_ID,
    u.Username
FROM [Task] t
JOIN [Student] s ON t.Student_ID = s.Student_ID
JOIN [User] u ON s.User_ID = u.User_ID
WHERE u.Email = 'ahmed.hasan@student.zewailcity.edu.eg'
ORDER BY t.Task_ID DESC;

PRINT '';
PRINT '============================================================';
PRINT 'Instructions:';
PRINT '1. Go to http://localhost:5000/reminders';
PRINT '2. Fill in Quick Add form:';
PRINT '   - Title: "Test Reminder from Website"';
PRINT '   - Date/Time: Tomorrow at 3:00 PM';
PRINT '   - Priority: High';
PRINT '3. Click "Create Reminder"';
PRINT '4. Come back and run this script again';
PRINT '============================================================';
PRINT '';
PRINT 'AFTER running the above, you should see a NEW row with:';
PRINT '  Task_Title = "Test Reminder from Website"';
PRINT '  Priority = "high"';
PRINT '  Status = "pending"';
PRINT '============================================================';
GO

