-- =============================================
-- Fix: Add Email column to Instructor table
-- =============================================
-- This script adds the missing Email column to the Instructor table
-- Run this in SQL Server Management Studio

USE unify;
GO

-- Check if Email column exists, if not, add it
IF NOT EXISTS (
    SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'Instructor' 
    AND COLUMN_NAME = 'Email'
)
BEGIN
    ALTER TABLE Instructor
    ADD Email VARCHAR(255) NULL;
    
    -- Add unique constraint if needed (optional, uncomment if you want unique emails)
    -- ALTER TABLE Instructor
    -- ADD CONSTRAINT UQ_Instructor_Email UNIQUE (Email);
    
    PRINT 'Email column added to Instructor table successfully.';
END
ELSE
BEGIN
    PRINT 'Email column already exists in Instructor table.';
END
GO

