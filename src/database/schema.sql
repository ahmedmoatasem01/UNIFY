-- Unify Database Schema (MySQL)
-- This file contains all table creation statements

USE unify;

-- =========================================
-- Table: User
-- =========================================
CREATE TABLE IF NOT EXISTS `User` (
    User_ID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(100) NOT NULL UNIQUE,
    Email VARCHAR(255) NOT NULL UNIQUE,
    Password_Hash VARCHAR(255) NOT NULL,
    Created_At DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (Email),
    INDEX idx_username (Username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: Student
-- =========================================
CREATE TABLE IF NOT EXISTS Student (
    Student_ID INT AUTO_INCREMENT PRIMARY KEY,
    User_ID INT NOT NULL,
    Department VARCHAR(100),
    Year_Level INT CHECK (Year_Level BETWEEN 1 AND 5),
    GPA FLOAT CHECK (GPA BETWEEN 0.0 AND 4.0),
    CONSTRAINT FK_Student_User FOREIGN KEY (User_ID)
        REFERENCES `User`(User_ID) ON DELETE CASCADE,
    INDEX idx_user_id (User_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: Instructor
-- =========================================
CREATE TABLE IF NOT EXISTS Instructor (
    Instructor_ID INT AUTO_INCREMENT PRIMARY KEY,
    User_ID INT NOT NULL,
    Department VARCHAR(100),
    Office VARCHAR(100),
    Email VARCHAR(255) UNIQUE,
    CONSTRAINT FK_Instructor_User FOREIGN KEY (User_ID)
        REFERENCES `User`(User_ID) ON DELETE CASCADE,
    INDEX idx_user_id (User_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: Course
-- =========================================
CREATE TABLE IF NOT EXISTS Course (
    Course_ID INT AUTO_INCREMENT PRIMARY KEY,
    Course_Name VARCHAR(200) NOT NULL,
    Credits INT NOT NULL,
    Instructor_ID INT NOT NULL,
    Schedule TEXT,
    CONSTRAINT FK_Course_Instructor FOREIGN KEY (Instructor_ID)
        REFERENCES Instructor(Instructor_ID) ON DELETE CASCADE,
    INDEX idx_instructor_id (Instructor_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: Enrollment
-- =========================================
CREATE TABLE IF NOT EXISTS Enrollment (
    Enrollment_ID INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID INT NOT NULL,
    Course_ID INT NOT NULL,
    Status VARCHAR(20) CHECK (Status IN ('enrolled', 'dropped', 'completed')),
    CONSTRAINT FK_Enroll_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE,
    CONSTRAINT FK_Enroll_Course FOREIGN KEY (Course_ID)
        REFERENCES Course(Course_ID) ON DELETE CASCADE,
    INDEX idx_student_id (Student_ID),
    INDEX idx_course_id (Course_ID),
    UNIQUE KEY unique_enrollment (Student_ID, Course_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: Task
-- =========================================
CREATE TABLE IF NOT EXISTS Task (
    Task_ID INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID INT NOT NULL,
    Task_Title VARCHAR(255) NOT NULL,
    Due_Date DATETIME NOT NULL,
    Priority VARCHAR(10) CHECK (Priority IN ('low','medium','high')),
    Status VARCHAR(20) CHECK (Status IN ('pending','completed')),
    CONSTRAINT FK_Task_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE,
    INDEX idx_student_id (Student_ID),
    INDEX idx_due_date (Due_Date),
    INDEX idx_status (Status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: Schedule
-- =========================================
CREATE TABLE IF NOT EXISTS Schedule (
    Schedule_ID INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID INT NOT NULL,
    Course_List TEXT,
    Optimized TINYINT(1) DEFAULT 0,
    CONSTRAINT FK_Schedule_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE,
    INDEX idx_student_id (Student_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: Note
-- =========================================
CREATE TABLE IF NOT EXISTS Note (
    Note_ID INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID INT NOT NULL,
    Original_File VARCHAR(255) NOT NULL,
    Summary_Text TEXT,
    Upload_Date DATETIME NOT NULL,
    CONSTRAINT FK_Note_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE,
    INDEX idx_student_id (Student_ID),
    INDEX idx_upload_date (Upload_Date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: Message
-- =========================================
CREATE TABLE IF NOT EXISTS Message (
    Message_ID INT AUTO_INCREMENT PRIMARY KEY,
    Sender_ID INT NOT NULL,
    Receiver_ID INT NOT NULL,
    Message_Text TEXT NOT NULL,
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT FK_Message_Sender FOREIGN KEY (Sender_ID)
        REFERENCES `User`(User_ID) ON DELETE CASCADE,
    CONSTRAINT FK_Message_Receiver FOREIGN KEY (Receiver_ID)
        REFERENCES `User`(User_ID) ON DELETE CASCADE,
    INDEX idx_sender_id (Sender_ID),
    INDEX idx_receiver_id (Receiver_ID),
    INDEX idx_timestamp (Timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: Transcript
-- =========================================
CREATE TABLE IF NOT EXISTS Transcript (
    Transcript_ID INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID INT NOT NULL,
    GPA FLOAT CHECK (GPA BETWEEN 0.0 AND 4.0),
    PDF_Path VARCHAR(255) NOT NULL,
    Issue_Date DATETIME NOT NULL,
    CONSTRAINT FK_Transcript_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE,
    INDEX idx_student_id (Student_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: Calendar
-- =========================================
CREATE TABLE IF NOT EXISTS Calendar (
    Event_ID INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID INT NOT NULL,
    Title VARCHAR(200) NOT NULL,
    Date DATE NOT NULL,
    Time TIME NOT NULL,
    Source VARCHAR(50),
    CONSTRAINT FK_Calendar_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE,
    INDEX idx_student_id (Student_ID),
    INDEX idx_date (Date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: Reminder
-- =========================================
CREATE TABLE IF NOT EXISTS Reminder (
    Reminder_ID INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID INT NOT NULL,
    Event_ID INT NOT NULL,
    Reminder_Time DATETIME NOT NULL,
    Status VARCHAR(10) CHECK (Status IN ('pending','done')),
    CONSTRAINT FK_Reminder_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE,
    CONSTRAINT FK_Reminder_Event FOREIGN KEY (Event_ID)
        REFERENCES Calendar(Event_ID) ON DELETE CASCADE,
    INDEX idx_student_id (Student_ID),
    INDEX idx_event_id (Event_ID),
    INDEX idx_reminder_time (Reminder_Time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: Focus_Session
-- =========================================
CREATE TABLE IF NOT EXISTS Focus_Session (
    Session_ID INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID INT NOT NULL,
    Duration INT NOT NULL,
    Start_Time DATETIME NOT NULL,
    End_Time DATETIME,
    Completed TINYINT(1) DEFAULT 0,
    CONSTRAINT FK_Focus_Student FOREIGN KEY (Student_ID)
        REFERENCES Student(Student_ID) ON DELETE CASCADE,
    INDEX idx_student_id (Student_ID),
    INDEX idx_start_time (Start_Time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: Teaching_Assistant
-- =========================================
CREATE TABLE IF NOT EXISTS Teaching_Assistant (
    TA_ID INT AUTO_INCREMENT PRIMARY KEY,
    User_ID INT NOT NULL,
    Assigned_Course_ID INT NOT NULL,
    Role VARCHAR(100) DEFAULT 'Teaching Assistant',
    Hours_Per_Week INT CHECK (Hours_Per_Week BETWEEN 1 AND 20),
    CONSTRAINT FK_TA_User FOREIGN KEY (User_ID)
        REFERENCES `User`(User_ID) ON DELETE CASCADE,
    CONSTRAINT FK_TA_Course FOREIGN KEY (Assigned_Course_ID)
        REFERENCES Course(Course_ID) ON DELETE CASCADE,
    INDEX idx_user_id (User_ID),
    INDEX idx_course_id (Assigned_Course_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
