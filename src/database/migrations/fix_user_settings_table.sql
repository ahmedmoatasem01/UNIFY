-- Fix User_Settings Table - Add Missing Columns
-- Run this script to update the User_Settings table structure

USE unify;
GO

-- Check if table exists
IF OBJECT_ID('User_Settings', 'U') IS NULL
BEGIN
    PRINT 'ERROR: User_Settings table does not exist. Please run create_user_settings_table.sql first.';
    RETURN;
END
GO

-- Add missing columns if they don't exist
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Settings' AND COLUMN_NAME = 'email_notifications')
BEGIN
    ALTER TABLE [User_Settings] ADD email_notifications BIT DEFAULT 1;
    PRINT 'Added column: email_notifications';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Settings' AND COLUMN_NAME = 'push_notifications')
BEGIN
    ALTER TABLE [User_Settings] ADD push_notifications BIT DEFAULT 1;
    PRINT 'Added column: push_notifications';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Settings' AND COLUMN_NAME = 'calendar_reminders')
BEGIN
    ALTER TABLE [User_Settings] ADD calendar_reminders BIT DEFAULT 1;
    PRINT 'Added column: calendar_reminders';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Settings' AND COLUMN_NAME = 'assignment_deadlines')
BEGIN
    ALTER TABLE [User_Settings] ADD assignment_deadlines BIT DEFAULT 1;
    PRINT 'Added column: assignment_deadlines';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Settings' AND COLUMN_NAME = 'sync_google_calendar')
BEGIN
    ALTER TABLE [User_Settings] ADD sync_google_calendar BIT DEFAULT 0;
    PRINT 'Added column: sync_google_calendar';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Settings' AND COLUMN_NAME = 'calendar_default_view')
BEGIN
    ALTER TABLE [User_Settings] ADD calendar_default_view VARCHAR(20) DEFAULT 'week';
    PRINT 'Added column: calendar_default_view';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Settings' AND COLUMN_NAME = 'timezone')
BEGIN
    ALTER TABLE [User_Settings] ADD timezone VARCHAR(50) DEFAULT 'Africa/Cairo';
    PRINT 'Added column: timezone';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Settings' AND COLUMN_NAME = 'theme')
BEGIN
    ALTER TABLE [User_Settings] ADD theme VARCHAR(10) DEFAULT 'dark';
    PRINT 'Added column: theme';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Settings' AND COLUMN_NAME = 'language')
BEGIN
    ALTER TABLE [User_Settings] ADD language VARCHAR(5) DEFAULT 'en';
    PRINT 'Added column: language';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Settings' AND COLUMN_NAME = 'colorblind_mode')
BEGIN
    ALTER TABLE [User_Settings] ADD colorblind_mode BIT DEFAULT 0;
    PRINT 'Added column: colorblind_mode';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Settings' AND COLUMN_NAME = 'dyslexia_font')
BEGIN
    ALTER TABLE [User_Settings] ADD dyslexia_font BIT DEFAULT 0;
    PRINT 'Added column: dyslexia_font';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Settings' AND COLUMN_NAME = 'profile_visibility')
BEGIN
    ALTER TABLE [User_Settings] ADD profile_visibility VARCHAR(20) DEFAULT 'public';
    PRINT 'Added column: profile_visibility';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Settings' AND COLUMN_NAME = 'share_schedule')
BEGIN
    ALTER TABLE [User_Settings] ADD share_schedule BIT DEFAULT 0;
    PRINT 'Added column: share_schedule';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Settings' AND COLUMN_NAME = 'created_at')
BEGIN
    ALTER TABLE [User_Settings] ADD created_at DATETIME DEFAULT GETDATE();
    PRINT 'Added column: created_at';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Settings' AND COLUMN_NAME = 'updated_at')
BEGIN
    ALTER TABLE [User_Settings] ADD updated_at DATETIME DEFAULT GETDATE();
    PRINT 'Added column: updated_at';
END
GO

-- Update existing rows with default values
UPDATE [User_Settings]
SET 
    email_notifications = 1,
    push_notifications = 1,
    calendar_reminders = 1,
    assignment_deadlines = 1,
    sync_google_calendar = 0,
    calendar_default_view = 'week',
    timezone = 'Africa/Cairo',
    theme = COALESCE(theme, 'dark'),
    language = COALESCE(language, 'en'),
    colorblind_mode = 0,
    dyslexia_font = 0,
    profile_visibility = 'public',
    share_schedule = 0,
    created_at = COALESCE(created_at, GETDATE()),
    updated_at = GETDATE()
WHERE email_notifications IS NULL 
   OR push_notifications IS NULL
   OR calendar_reminders IS NULL;
GO

PRINT '';
PRINT '✅ User_Settings table structure has been updated successfully!';
PRINT '';
GO

