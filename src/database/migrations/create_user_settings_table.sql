-- Create User_Settings Table for UNIFY
-- SQL Server syntax

USE unify;
GO

-- Check if table exists and drop it
IF OBJECT_ID('dbo.User_Settings', 'U') IS NOT NULL
    DROP TABLE dbo.User_Settings;
GO

-- Create User_Settings table
CREATE TABLE [User_Settings] (
    Setting_ID INT PRIMARY KEY IDENTITY(1,1),
    User_ID INT NOT NULL UNIQUE,
    
    -- Notification Settings
    email_notifications BIT DEFAULT 1,
    push_notifications BIT DEFAULT 1,
    calendar_reminders BIT DEFAULT 1,
    assignment_deadlines BIT DEFAULT 1,
    
    -- Calendar Settings
    sync_google_calendar BIT DEFAULT 0,
    calendar_default_view VARCHAR(20) DEFAULT 'week',
    timezone VARCHAR(50) DEFAULT 'Africa/Cairo',
    
    -- Appearance Settings
    theme VARCHAR(10) DEFAULT 'dark',
    language VARCHAR(5) DEFAULT 'en',
    colorblind_mode BIT DEFAULT 0,
    dyslexia_font BIT DEFAULT 0,
    
    -- Privacy Settings
    profile_visibility VARCHAR(20) DEFAULT 'public',
    share_schedule BIT DEFAULT 0,
    
    -- Timestamps
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    
    -- Foreign Key
    CONSTRAINT FK_UserSettings_User FOREIGN KEY (User_ID)
        REFERENCES [User](User_ID) ON DELETE CASCADE
);
GO

-- Create index for faster lookups
CREATE INDEX idx_user_settings_user_id ON [User_Settings](User_ID);
GO

-- Insert default settings for existing users
INSERT INTO [User_Settings] (User_ID)
SELECT User_ID FROM [User]
WHERE User_ID NOT IN (SELECT User_ID FROM [User_Settings]);
GO

PRINT '✅ User_Settings table created successfully!';
PRINT '✅ Default settings added for existing users!';
GO

