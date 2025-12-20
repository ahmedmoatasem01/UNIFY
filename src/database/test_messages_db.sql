-- Test Messages Feature Database
-- Run this to check if Message table exists and has data

USE unify;
GO

PRINT '============================================================';
PRINT 'Messages Feature - Database Check';
PRINT '============================================================';
PRINT '';

-- Check if Message table exists
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'Message')
BEGIN
    PRINT '✅ Message table EXISTS';
    PRINT '';
    
    -- Check structure
    PRINT 'Table Structure:';
    SELECT 
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'Message'
    ORDER BY ORDINAL_POSITION;
    
    PRINT '';
    PRINT 'Message Count:';
    SELECT COUNT(*) as Total_Messages FROM [Message];
    
    PRINT '';
    PRINT 'Sample Messages:';
    SELECT TOP 5 
        Message_ID,
        Sender_ID,
        Receiver_ID,
        LEFT(Message_Text, 50) as Message_Preview,
        Timestamp,
        Is_Read
    FROM [Message]
    ORDER BY Message_ID DESC;
    
    PRINT '';
    PRINT 'Users who can send messages:';
    SELECT User_ID, Username, Email FROM [User];
    
END
ELSE
BEGIN
    PRINT '❌ Message table DOES NOT EXIST!';
    PRINT '';
    PRINT 'Run this to create it:';
    PRINT '';
    PRINT 'CREATE TABLE Message (';
    PRINT '    Message_ID INT IDENTITY(1,1) PRIMARY KEY,';
    PRINT '    Sender_ID INT NOT NULL,';
    PRINT '    Receiver_ID INT NOT NULL,';
    PRINT '    Message_Text NVARCHAR(MAX) NOT NULL,';
    PRINT '    Timestamp DATETIME DEFAULT GETDATE(),';
    PRINT '    Is_Read BIT DEFAULT 0,';
    PRINT '    FOREIGN KEY (Sender_ID) REFERENCES [User](User_ID) ON DELETE CASCADE,';
    PRINT '    FOREIGN KEY (Receiver_ID) REFERENCES [User](User_ID) ON DELETE CASCADE';
    PRINT ');';
END

GO

