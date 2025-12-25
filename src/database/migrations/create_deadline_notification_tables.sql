-- Create Deadline Notification Tables for UNIFY
-- SQL Server syntax

USE unify;
GO

-- =========================================
-- Table: DeadlineNotification
-- =========================================
IF OBJECT_ID('dbo.DeadlineNotification', 'U') IS NOT NULL
    DROP TABLE dbo.DeadlineNotification;
GO

CREATE TABLE [DeadlineNotification] (
    Notification_ID INT PRIMARY KEY IDENTITY(1,1),
    User_ID INT NOT NULL,
    Deadline_Type NVARCHAR(50) NOT NULL,  -- 'task', 'assignment', 'exam', 'project', 'calendar'
    Source_ID INT NOT NULL,  -- ID of the task, assignment, or event
    Source_Type NVARCHAR(50) NOT NULL,  -- 'task', 'assignment', 'calendar_event'
    Deadline_Date DATETIME NOT NULL,
    Title NVARCHAR(255) NOT NULL,
    Description NVARCHAR(MAX),
    Priority NVARCHAR(20) CHECK (Priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
    Status NVARCHAR(20) CHECK (Status IN ('active', 'completed', 'overdue', 'cancelled')) DEFAULT 'active',
    Created_At DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_DeadlineNotification_User FOREIGN KEY (User_ID)
        REFERENCES [User](User_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_deadline_notification_user_id ON [DeadlineNotification](User_ID);
CREATE INDEX idx_deadline_notification_deadline_date ON [DeadlineNotification](Deadline_Date);
CREATE INDEX idx_deadline_notification_status ON [DeadlineNotification](Status);
CREATE INDEX idx_deadline_notification_source ON [DeadlineNotification](Source_Type, Source_ID);
GO

-- =========================================
-- Table: DeadlineAlertSchedule
-- =========================================
IF OBJECT_ID('dbo.DeadlineAlertSchedule', 'U') IS NOT NULL
    DROP TABLE dbo.DeadlineAlertSchedule;
GO

CREATE TABLE [DeadlineAlertSchedule] (
    Schedule_ID INT PRIMARY KEY IDENTITY(1,1),
    Notification_ID INT NOT NULL,
    Alert_Time_Before_Deadline INT NOT NULL,  -- Minutes before deadline
    Alert_Type NVARCHAR(50),  -- 'in_app', 'email', 'push'
    Is_Sent BIT DEFAULT 0,
    Sent_At DATETIME,
    CONSTRAINT FK_DeadlineAlertSchedule_Notification FOREIGN KEY (Notification_ID)
        REFERENCES [DeadlineNotification](Notification_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_deadline_alert_schedule_notification_id ON [DeadlineAlertSchedule](Notification_ID);
CREATE INDEX idx_deadline_alert_schedule_is_sent ON [DeadlineAlertSchedule](Is_Sent);
GO

-- =========================================
-- Table: DeadlineNotificationPreference
-- =========================================
IF OBJECT_ID('dbo.DeadlineNotificationPreference', 'U') IS NOT NULL
    DROP TABLE dbo.DeadlineNotificationPreference;
GO

CREATE TABLE [DeadlineNotificationPreference] (
    Preference_ID INT PRIMARY KEY IDENTITY(1,1),
    User_ID INT NOT NULL,
    Deadline_Type NVARCHAR(50),  -- 'task', 'assignment', 'exam', 'all'
    Alert_Intervals NVARCHAR(MAX),  -- JSON array: [4320, 1440, 60] (minutes before)
    Email_Enabled BIT DEFAULT 0,
    In_App_Enabled BIT DEFAULT 1,
    Quiet_Hours_Start TIME,
    Quiet_Hours_End TIME,
    CONSTRAINT FK_DeadlineNotificationPreference_User FOREIGN KEY (User_ID)
        REFERENCES [User](User_ID) ON DELETE CASCADE,
    CONSTRAINT UQ_DeadlineNotificationPreference_User_Type UNIQUE (User_ID, Deadline_Type)
);
GO

CREATE INDEX idx_deadline_notification_preference_user_id ON [DeadlineNotificationPreference](User_ID);
GO

PRINT '✅ DeadlineNotification tables created successfully!';
GO

