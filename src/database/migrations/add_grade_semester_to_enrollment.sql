-- Migration: Add Grade and Semester columns to Enrollment table
-- Run this script to update your existing database

USE unify;

-- Add Grade column if it doesn't exist
ALTER TABLE Enrollment 
ADD COLUMN IF NOT EXISTS Grade VARCHAR(5) DEFAULT NULL;

-- Add Semester column if it doesn't exist
ALTER TABLE Enrollment 
ADD COLUMN IF NOT EXISTS Semester VARCHAR(50) DEFAULT NULL;

-- Optional: Update existing enrollments with sample data (for testing)
-- Uncomment the lines below if you want to populate sample grades

/*
-- Sample update for testing (update based on your actual data)
UPDATE Enrollment 
SET Grade = 'A', Semester = 'Fall 2023'
WHERE Status = 'completed' AND Grade IS NULL;
*/

