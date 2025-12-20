-- =============================================
-- Course Materials Management Table
-- =============================================
-- This table stores course materials uploaded by instructors
-- Materials can be files (PDFs, PowerPoints, videos) or links
-- Supports organization by week and topic

USE unify;
GO

-- Check if table exists, drop if needed (for development)
IF OBJECT_ID('CourseMaterial', 'U') IS NOT NULL
    DROP TABLE CourseMaterial;
GO

CREATE TABLE CourseMaterial (
    Material_ID INT IDENTITY(1,1) PRIMARY KEY,
    Course_ID INT NOT NULL,
    Instructor_ID INT NOT NULL,
    Material_Title VARCHAR(255) NOT NULL,
    Material_Type VARCHAR(50) NOT NULL,
    File_Path VARCHAR(500) NULL,  -- Path to uploaded file (NULL for links)
    Link_URL VARCHAR(500) NULL,   -- URL for external links (NULL for files)
    Description TEXT NULL,
    Week_Number INT NULL,         -- Week number for organization
    Topic VARCHAR(200) NULL,       -- Topic/topic name for organization
    Upload_Date DATETIME NOT NULL DEFAULT GETDATE(),
    File_Size BIGINT NULL,        -- File size in bytes
    Download_Count INT DEFAULT 0,
    Is_Active BIT DEFAULT 1,      -- Soft delete flag (1 = active, 0 = deleted)
    
    CONSTRAINT FK_CourseMaterial_Course FOREIGN KEY (Course_ID)
        REFERENCES Course(Course_ID) ON DELETE CASCADE,
    CONSTRAINT FK_CourseMaterial_Instructor FOREIGN KEY (Instructor_ID)
        REFERENCES Instructor(Instructor_ID) ON DELETE CASCADE,
    
    INDEX idx_course_id (Course_ID),
    INDEX idx_instructor_id (Instructor_ID),
    INDEX idx_week_number (Week_Number),
    INDEX idx_material_type (Material_Type),
    INDEX idx_upload_date (Upload_Date),
    INDEX idx_is_active (Is_Active)
);
GO

PRINT 'CourseMaterial table created successfully.';
GO

