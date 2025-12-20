-- Create unify database if it doesn't exist
-- Run this script in SQL Server Management Studio

-- Check if database exists
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'unify')
BEGIN
    CREATE DATABASE unify;
    PRINT 'Database "unify" created successfully.';
END
ELSE
BEGIN
    PRINT 'Database "unify" already exists.';
END
GO

-- Use the database
USE unify;
GO

PRINT 'Now connected to unify database.';
PRINT 'You can now run the CourseMaterial table creation script.';
GO

