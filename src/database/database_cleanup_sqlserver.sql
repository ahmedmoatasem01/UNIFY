-- ============================================================
-- SQL SERVER Cleanup Script - Delete in Correct Order
-- Run this to clear all data and start fresh
-- ============================================================

USE unify;
GO

PRINT 'Starting cleanup...';

-- Delete in reverse dependency order (children first, parents last)

-- Level 1: Tables that depend on Calendar
PRINT 'Deleting Reminders...';
DELETE FROM Reminder;

-- Level 2: Tables that depend on Student/Course but not each other
PRINT 'Deleting Calendar events...';
DELETE FROM Calendar;

PRINT 'Deleting Tasks...';
DELETE FROM Task;

PRINT 'Deleting Notes...';
DELETE FROM Note;

PRINT 'Deleting Schedules...';
DELETE FROM Schedule;

PRINT 'Deleting Focus Sessions...';
DELETE FROM Focus_Session;

PRINT 'Deleting Transcripts...';
DELETE FROM Transcript;

PRINT 'Deleting Enrollments...';
DELETE FROM Enrollment;

-- Level 3: Tables that depend on Course
PRINT 'Deleting Teaching Assistants...';
DELETE FROM Teaching_Assistant;

PRINT 'Deleting Courses...';
DELETE FROM Course;

-- Level 4: Tables that depend on User
PRINT 'Deleting Messages...';
DELETE FROM Message;

PRINT 'Deleting Instructors...';
DELETE FROM Instructor;

PRINT 'Deleting Students...';
DELETE FROM Student;

-- Level 5: Root table
PRINT 'Deleting Users...';
DELETE FROM [User];

PRINT '';
PRINT '============================================================';
PRINT 'Cleanup complete! All tables are now empty.';
PRINT 'You can now run the sample data script.';
PRINT '============================================================';
GO

