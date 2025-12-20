-- =============================================
-- UNIFY DATABASE - COMPLETE SETUP SCRIPT
-- SQL Server Syntax
-- =============================================
-- This script creates the unify database and all tables
-- Run this entire script in SQL Server Management Studio (SSMS)
-- =============================================

-- =============================================
-- STEP 1: CREATE DATABASE
-- =============================================
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

-- =============================================
-- STEP 2: DROP TABLES IF THEY EXIST (FOR REBUILD)
-- =============================================
-- Drop tables in reverse dependency order
IF OBJECT_ID('CourseMaterial', 'U') IS NOT NULL DROP TABLE CourseMaterial;
IF OBJECT_ID('Course_Schedule_Slot', 'U') IS NOT NULL DROP TABLE Course_Schedule_Slot;
IF OBJECT_ID('User_Settings', 'U') IS NOT NULL DROP TABLE User_Settings;
IF OBJECT_ID('Reminder', 'U') IS NOT NULL DROP TABLE Reminder;
IF OBJECT_ID('Focus_Session', 'U') IS NOT NULL DROP TABLE Focus_Session;
IF OBJECT_ID('Calendar', 'U') IS NOT NULL DROP TABLE Calendar;
IF OBJECT_ID('Transcript', 'U') IS NOT NULL DROP TABLE Transcript;
IF OBJECT_ID('Message', 'U') IS NOT NULL DROP TABLE Message;
IF OBJECT_ID('Note', 'U') IS NOT NULL DROP TABLE Note;
IF OBJECT_ID('Task', 'U') IS NOT NULL DROP TABLE Task;
IF OBJECT_ID('Schedule', 'U') IS NOT NULL DROP TABLE Schedule;
IF OBJECT_ID('Enrollment', 'U') IS NOT NULL DROP TABLE Enrollment;
IF OBJECT_ID('Teaching_Assistant', 'U') IS NOT NULL DROP TABLE Teaching_Assistant;
IF OBJECT_ID('Course', 'U') IS NOT NULL DROP TABLE Course;
IF OBJECT_ID('Instructor', 'U') IS NOT NULL DROP TABLE Instructor;
IF OBJECT_ID('Student', 'U') IS NOT NULL DROP TABLE Student;
IF OBJECT_ID('[User]', 'U') IS NOT NULL DROP TABLE [User];
GO

-- =============================================
-- STEP 3: CREATE TABLES
-- =============================================

-- =========================================
-- Table: User
-- =========================================
CREATE TABLE [User] (
    User_ID INT IDENTITY(1,1) PRIMARY KEY,
    Username VARCHAR(100) NOT NULL UNIQUE,
    Email VARCHAR(255) NOT NULL UNIQUE,
    Password_Hash VARCHAR(255) NOT NULL,
    Created_At DATETIME NOT NULL DEFAULT GETDATE()
);
GO

CREATE INDEX idx_email ON [User](Email);
CREATE INDEX idx_username ON [User](Username);
GO

PRINT 'Table [User] created successfully.';
GO

-- =========================================
-- Table: Student
-- =========================================
CREATE TABLE Student (
    Student_ID INT IDENTITY(1,1) PRIMARY KEY,
    User_ID INT NOT NULL,
    Department VARCHAR(100),
    Year_Level INT CHECK (Year_Level BETWEEN 1 AND 5),
    GPA FLOAT CHECK (GPA BETWEEN 0.0 AND 4.0),
    CONSTRAINT FK_Student_User FOREIGN KEY (User_ID)
        REFERENCES [User](User_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_user_id ON Student(User_ID);
GO

PRINT 'Table Student created successfully.';
GO

-- =========================================
-- Table: Instructor
-- =========================================
CREATE TABLE Instructor (
    Instructor_ID INT IDENTITY(1,1) PRIMARY KEY,
    User_ID INT NOT NULL,
    Department VARCHAR(100),
    Office VARCHAR(100),
    Email VARCHAR(255) NULL,  -- Added Email column
    CONSTRAINT FK_Instructor_User FOREIGN KEY (User_ID)
        REFERENCES [User](User_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_user_id ON Instructor(User_ID);
GO

PRINT 'Table Instructor created successfully.';
GO

-- =========================================
-- Table: Course
-- =========================================
CREATE TABLE Course (
    Course_ID INT IDENTITY(1,1) PRIMARY KEY,
    Course_Name VARCHAR(200) NOT NULL,
    Credits INT NOT NULL,
    Instructor_ID INT NOT NULL,
    Schedule TEXT,
    CONSTRAINT FK_Course_Instructor FOREIGN KEY (Instructor_ID)
        REFERENCES Instructor(Instructor_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_instructor_id ON Course(Instructor_ID);
GO

PRINT 'Table Course created successfully.';
GO

-- =========================================
-- Table: Enrollment
-- =========================================
CREATE TABLE Enrollment (
    Enrollment_ID INT IDENTITY(1,1) PRIMARY KEY,
    Student_ID INT NOT NULL,
    Course_ID INT NOT NULL,
    Status VARCHAR(20) CHECK (Status IN ('enrolled', 'dropped', 'completed')),
    Grade VARCHAR(5) NULL,
    Semester VARCHAR(50) NULL,
    CONSTRAINT FK_Enroll_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE,
    CONSTRAINT FK_Enroll_Course FOREIGN KEY (Course_ID)
        REFERENCES Course(Course_ID) ON DELETE CASCADE,
    CONSTRAINT unique_enrollment UNIQUE (Student_ID, Course_ID)
);
GO

CREATE INDEX idx_student_id ON Enrollment(Student_ID);
CREATE INDEX idx_course_id ON Enrollment(Course_ID);
GO

PRINT 'Table Enrollment created successfully.';
GO

-- =========================================
-- Table: Task
-- =========================================
CREATE TABLE Task (
    Task_ID INT IDENTITY(1,1) PRIMARY KEY,
    Student_ID INT NOT NULL,
    Task_Title VARCHAR(255) NOT NULL,
    Due_Date DATETIME NOT NULL,
    Priority VARCHAR(10) CHECK (Priority IN ('low','medium','high')),
    Status VARCHAR(20) CHECK (Status IN ('pending','completed')),
    CONSTRAINT FK_Task_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_student_id ON Task(Student_ID);
CREATE INDEX idx_due_date ON Task(Due_Date);
CREATE INDEX idx_status ON Task(Status);
GO

PRINT 'Table Task created successfully.';
GO

-- =========================================
-- Table: Schedule
-- =========================================
CREATE TABLE Schedule (
    Schedule_ID INT IDENTITY(1,1) PRIMARY KEY,
    Student_ID INT NOT NULL,
    Course_List TEXT,
    Optimized BIT DEFAULT 0,
    CONSTRAINT FK_Schedule_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_student_id ON Schedule(Student_ID);
GO

PRINT 'Table Schedule created successfully.';
GO

-- =========================================
-- Table: Note
-- =========================================
CREATE TABLE Note (
    Note_ID INT IDENTITY(1,1) PRIMARY KEY,
    Student_ID INT NOT NULL,
    Original_File VARCHAR(255) NOT NULL,
    Summary_Text TEXT,
    Upload_Date DATETIME NOT NULL,
    CONSTRAINT FK_Note_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_student_id ON Note(Student_ID);
CREATE INDEX idx_upload_date ON Note(Upload_Date);
GO

PRINT 'Table Note created successfully.';
GO

-- =========================================
-- Table: Message
-- =========================================
CREATE TABLE Message (
    Message_ID INT IDENTITY(1,1) PRIMARY KEY,
    Sender_ID INT NOT NULL,
    Receiver_ID INT NOT NULL,
    Message_Text TEXT NOT NULL,
    Timestamp DATETIME NOT NULL DEFAULT GETDATE(),
    Is_Read BIT DEFAULT 0,
    CONSTRAINT FK_Message_Sender FOREIGN KEY (Sender_ID)
        REFERENCES [User](User_ID) ON DELETE CASCADE,
    CONSTRAINT FK_Message_Receiver FOREIGN KEY (Receiver_ID)
        REFERENCES [User](User_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_sender_id ON Message(Sender_ID);
CREATE INDEX idx_receiver_id ON Message(Receiver_ID);
CREATE INDEX idx_timestamp ON Message(Timestamp);
CREATE INDEX idx_is_read ON Message(Is_Read);
GO

PRINT 'Table Message created successfully.';
GO

-- =========================================
-- Table: Transcript
-- =========================================
CREATE TABLE Transcript (
    Transcript_ID INT IDENTITY(1,1) PRIMARY KEY,
    Student_ID INT NOT NULL,
    GPA FLOAT CHECK (GPA BETWEEN 0.0 AND 4.0),
    PDF_Path VARCHAR(255) NOT NULL,
    Issue_Date DATETIME NOT NULL,
    CONSTRAINT FK_Transcript_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_student_id ON Transcript(Student_ID);
GO

PRINT 'Table Transcript created successfully.';
GO

-- =========================================
-- Table: Calendar
-- =========================================
CREATE TABLE Calendar (
    Event_ID INT IDENTITY(1,1) PRIMARY KEY,
    Student_ID INT NOT NULL,
    Title VARCHAR(200) NOT NULL,
    Date DATE NOT NULL,
    Time TIME NOT NULL,
    Source VARCHAR(50),
    CONSTRAINT FK_Calendar_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_student_id ON Calendar(Student_ID);
CREATE INDEX idx_date ON Calendar(Date);
GO

PRINT 'Table Calendar created successfully.';
GO

-- =========================================
-- Table: Reminder
-- =========================================
CREATE TABLE Reminder (
    Reminder_ID INT IDENTITY(1,1) PRIMARY KEY,
    Student_ID INT NOT NULL,
    Event_ID INT NOT NULL,
    Reminder_Time DATETIME NOT NULL,
    Status VARCHAR(10) CHECK (Status IN ('pending','done')),
    CONSTRAINT FK_Reminder_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE,
    CONSTRAINT FK_Reminder_Event FOREIGN KEY (Event_ID)
        REFERENCES Calendar(Event_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_student_id ON Reminder(Student_ID);
CREATE INDEX idx_event_id ON Reminder(Event_ID);
CREATE INDEX idx_reminder_time ON Reminder(Reminder_Time);
GO

PRINT 'Table Reminder created successfully.';
GO

-- =========================================
-- Table: Focus_Session
-- =========================================
CREATE TABLE Focus_Session (
    Session_ID INT IDENTITY(1,1) PRIMARY KEY,
    Student_ID INT NOT NULL,
    Duration INT NOT NULL,
    Start_Time DATETIME NOT NULL,
    End_Time DATETIME NULL,
    Completed BIT DEFAULT 0,
    CONSTRAINT FK_Focus_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_student_id ON Focus_Session(Student_ID);
CREATE INDEX idx_start_time ON Focus_Session(Start_Time);
GO

PRINT 'Table Focus_Session created successfully.';
GO

-- =========================================
-- Table: Teaching_Assistant
-- =========================================
CREATE TABLE Teaching_Assistant (
    TA_ID INT IDENTITY(1,1) PRIMARY KEY,
    User_ID INT NOT NULL,
    Assigned_Course_ID INT NOT NULL,
    Role VARCHAR(100) DEFAULT 'Teaching Assistant',
    Hours_Per_Week INT CHECK (Hours_Per_Week BETWEEN 1 AND 20),
    CONSTRAINT FK_TA_User FOREIGN KEY (User_ID)
        REFERENCES [User](User_ID) ON DELETE CASCADE,
    CONSTRAINT FK_TA_Course FOREIGN KEY (Assigned_Course_ID)
        REFERENCES Course(Course_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_user_id ON Teaching_Assistant(User_ID);
CREATE INDEX idx_course_id ON Teaching_Assistant(Assigned_Course_ID);
GO

PRINT 'Table Teaching_Assistant created successfully.';
GO

-- =========================================
-- Table: CourseMaterial
-- =========================================
CREATE TABLE CourseMaterial (
    Material_ID INT IDENTITY(1,1) PRIMARY KEY,
    Course_ID INT NOT NULL,
    Instructor_ID INT NOT NULL,
    Material_Title VARCHAR(255) NOT NULL,
    Material_Type VARCHAR(50) NOT NULL,
    File_Path VARCHAR(500) NULL,
    Link_URL VARCHAR(500) NULL,
    Description TEXT NULL,
    Week_Number INT NULL,
    Topic VARCHAR(200) NULL,
    Upload_Date DATETIME NOT NULL DEFAULT GETDATE(),
    File_Size BIGINT NULL,
    Download_Count INT DEFAULT 0,
    Is_Active BIT DEFAULT 1,
    CONSTRAINT FK_CourseMaterial_Course FOREIGN KEY (Course_ID)
        REFERENCES Course(Course_ID) ON DELETE CASCADE,
    CONSTRAINT FK_CourseMaterial_Instructor FOREIGN KEY (Instructor_ID)
        REFERENCES Instructor(Instructor_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_course_id ON CourseMaterial(Course_ID);
CREATE INDEX idx_instructor_id ON CourseMaterial(Instructor_ID);
CREATE INDEX idx_week_number ON CourseMaterial(Week_Number);
CREATE INDEX idx_material_type ON CourseMaterial(Material_Type);
CREATE INDEX idx_upload_date ON CourseMaterial(Upload_Date);
CREATE INDEX idx_is_active ON CourseMaterial(Is_Active);
GO

PRINT 'Table CourseMaterial created successfully.';
GO

-- =========================================
-- Table: User_Settings
-- =========================================
CREATE TABLE User_Settings (
    Setting_ID INT IDENTITY(1,1) PRIMARY KEY,
    User_ID INT NOT NULL UNIQUE,
    email_notifications BIT DEFAULT 1,
    push_notifications BIT DEFAULT 1,
    calendar_reminders BIT DEFAULT 1,
    assignment_deadlines BIT DEFAULT 1,
    sync_google_calendar BIT DEFAULT 0,
    calendar_default_view VARCHAR(20) DEFAULT 'week',
    timezone VARCHAR(50) DEFAULT 'Africa/Cairo',
    theme VARCHAR(10) DEFAULT 'dark',
    language VARCHAR(5) DEFAULT 'en',
    colorblind_mode BIT DEFAULT 0,
    dyslexia_font BIT DEFAULT 0,
    profile_visibility VARCHAR(20) DEFAULT 'public',
    share_schedule BIT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_UserSettings_User FOREIGN KEY (User_ID)
        REFERENCES [User](User_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_user_settings_user_id ON User_Settings(User_ID);
GO

PRINT 'Table User_Settings created successfully.';
GO

-- =========================================
-- Table: Course_Schedule_Slot
-- =========================================
CREATE TABLE Course_Schedule_Slot (
    Slot_ID INT IDENTITY(1,1) PRIMARY KEY,
    Course_ID INT NOT NULL,
    Course_Code VARCHAR(50) NOT NULL,
    Section INT NOT NULL,
    Day VARCHAR(10) NOT NULL,
    Start_Time TIME NOT NULL,
    End_Time TIME NOT NULL,
    Slot_Type VARCHAR(20) NOT NULL,
    Sub_Type VARCHAR(10) NULL,
    Academic_Year INT NULL,
    Term VARCHAR(20) NULL,
    CONSTRAINT FK_Slot_Course FOREIGN KEY (Course_ID)
        REFERENCES Course(Course_ID) ON DELETE CASCADE
);
GO

CREATE INDEX idx_course_code ON Course_Schedule_Slot(Course_Code);
CREATE INDEX idx_course_id ON Course_Schedule_Slot(Course_ID);
CREATE INDEX idx_day_time ON Course_Schedule_Slot(Day, Start_Time);
GO

PRINT 'Table Course_Schedule_Slot created successfully.';
GO

-- =============================================
-- STEP 4: VERIFICATION
-- =============================================
PRINT '';
PRINT '========================================';
PRINT 'DATABASE SETUP COMPLETE!';
PRINT '========================================';
PRINT '';

-- Show all tables
SELECT 
    TABLE_NAME,
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_NAME = t.TABLE_NAME) AS Column_Count
FROM INFORMATION_SCHEMA.TABLES t
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

PRINT '';
PRINT 'All tables have been created successfully.';
PRINT 'You can now start using the unify database.';
GO
