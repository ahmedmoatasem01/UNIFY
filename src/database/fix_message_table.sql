-- Fix Message Table - Add Is_Read Column
-- Run this in SSMS to add the missing column

USE unify;
GO

PRINT '============================================================';
PRINT 'Fixing Message Table';
PRINT '============================================================';

-- Check if Is_Read column exists
IF NOT EXISTS (
    SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'Message' AND COLUMN_NAME = 'Is_Read'
)
BEGIN
    PRINT 'Adding Is_Read column...';
    
    ALTER TABLE [Message]
    ADD Is_Read BIT DEFAULT 0;
    
    PRINT '✅ Is_Read column added successfully!';
END
ELSE
BEGIN
    PRINT '✅ Is_Read column already exists';
END

PRINT '';
PRINT 'Current Message table structure:';
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Message'
ORDER BY ORDINAL_POSITION;

GO

