-- ============================================================
-- Verify Course Import - Check what was imported
-- ============================================================

USE unify;
GO

PRINT '============================================================';
PRINT 'VERIFICATION: Imported Course Data';
PRINT '============================================================';
PRINT '';

-- Check Courses
PRINT '1. COURSES in Course table:';
SELECT COUNT(*) as Total_Courses FROM Course;

PRINT '';
PRINT 'Sample Courses (First 20):';
SELECT TOP 20 Course_ID, Course_Name, Credits, Instructor_ID 
FROM Course 
ORDER BY Course_Name;

PRINT '';
PRINT '2. SCHEDULE SLOTS in Course_Schedule_Slot table:';
SELECT COUNT(*) as Total_Slots FROM Course_Schedule_Slot;

PRINT '';
PRINT 'Slots by Course Code (showing variety):';
SELECT 
    Course_Code, 
    COUNT(*) as Slot_Count,
    COUNT(DISTINCT Section) as Sections
FROM Course_Schedule_Slot
GROUP BY Course_Code
ORDER BY Course_Code;

PRINT '';
PRINT 'Sample Schedule Slots (First 10):';
SELECT TOP 10 
    Slot_ID,
    Course_Code,
    Section,
    Day,
    CAST(Start_Time AS VARCHAR(5)) as Start_Time,
    CAST(End_Time AS VARCHAR(5)) as End_Time,
    Slot_Type,
    Sub_Type
FROM Course_Schedule_Slot
ORDER BY Course_Code, Section, Day, Start_Time;

PRINT '';
PRINT '============================================================';
PRINT 'Import Status:';
PRINT '';
PRINT 'If you see:';
PRINT '  - 292 courses in Course table';
PRINT '  - 702 slots in Course_Schedule_Slot table';
PRINT '';
PRINT 'Then the import was SUCCESSFUL!';
PRINT '';
PRINT 'Next step: Go to http://localhost:5000/course-registration';
PRINT 'and search for courses like CSAI, MATH, PHYS, etc.';
PRINT '============================================================';
GO

