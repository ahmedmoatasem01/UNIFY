-- ============================================================================
-- Smart Study Plan Generator - Database Schema
-- FR-AI-4: AI-Powered Study Planning System
-- ============================================================================

-- Study Plan Table
-- Stores personalized study plans for students
CREATE TABLE StudyPlan (
    Plan_ID INT IDENTITY(1,1) PRIMARY KEY,
    Student_ID INT NOT NULL,
    Course_ID INT,
    Plan_Name NVARCHAR(255) NOT NULL,
    Start_Date DATE NOT NULL,
    End_Date DATE NOT NULL,
    Status NVARCHAR(20) CHECK (Status IN ('active', 'paused', 'completed', 'archived')) DEFAULT 'active',
    Completion_Percentage DECIMAL(5,2) DEFAULT 0,
    Created_At DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID) ON DELETE CASCADE,
    FOREIGN KEY (Course_ID) REFERENCES Course(Course_ID) ON DELETE SET NULL
);

-- Create indexes for better query performance
CREATE INDEX IX_StudyPlan_Student ON StudyPlan(Student_ID);
CREATE INDEX IX_StudyPlan_Course ON StudyPlan(Course_ID);
CREATE INDEX IX_StudyPlan_Status ON StudyPlan(Status);
CREATE INDEX IX_StudyPlan_Dates ON StudyPlan(Start_Date, End_Date);

-- Study Task Table
-- Stores individual tasks within study plans with hierarchical support
CREATE TABLE StudyTask (
    Task_ID INT IDENTITY(1,1) PRIMARY KEY,
    Plan_ID INT NOT NULL,
    Parent_Task_ID INT,  -- For subtasks (self-referencing)
    Task_Title NVARCHAR(255) NOT NULL,
    Description NVARCHAR(MAX),
    Estimated_Hours DECIMAL(4,1),
    Actual_Hours DECIMAL(4,1),
    Due_Date DATETIME,
    Priority NVARCHAR(10) CHECK (Priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
    Status NVARCHAR(20) CHECK (Status IN ('pending', 'in_progress', 'completed', 'skipped')) DEFAULT 'pending',
    Suggested_Resources NVARCHAR(MAX),  -- JSON array of resource links
    Created_At DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (Plan_ID) REFERENCES StudyPlan(Plan_ID) ON DELETE CASCADE,
    FOREIGN KEY (Parent_Task_ID) REFERENCES StudyTask(Task_ID) ON DELETE NO ACTION
);

-- Create indexes for better query performance
CREATE INDEX IX_StudyTask_Plan ON StudyTask(Plan_ID);
CREATE INDEX IX_StudyTask_Parent ON StudyTask(Parent_Task_ID);
CREATE INDEX IX_StudyTask_Status ON StudyTask(Status);
CREATE INDEX IX_StudyTask_DueDate ON StudyTask(Due_Date);
CREATE INDEX IX_StudyTask_Priority ON StudyTask(Priority);

-- Study Recommendation Table
-- Stores AI-generated resource recommendations
CREATE TABLE StudyRecommendation (
    Recommendation_ID INT IDENTITY(1,1) PRIMARY KEY,
    Student_ID INT NOT NULL,
    Course_ID INT,
    Topic NVARCHAR(255),
    Resource_Type NVARCHAR(50),  -- 'note', 'video', 'practice', 'textbook'
    Resource_Link NVARCHAR(500),
    Reason NVARCHAR(MAX),
    Relevance_Score DECIMAL(3,2),  -- 0.00 to 1.00
    Generated_At DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID) ON DELETE CASCADE,
    FOREIGN KEY (Course_ID) REFERENCES Course(Course_ID) ON DELETE SET NULL
);

-- Create indexes for better query performance
CREATE INDEX IX_StudyRecommendation_Student ON StudyRecommendation(Student_ID);
CREATE INDEX IX_StudyRecommendation_Course ON StudyRecommendation(Course_ID);
CREATE INDEX IX_StudyRecommendation_Type ON StudyRecommendation(Resource_Type);
CREATE INDEX IX_StudyRecommendation_Score ON StudyRecommendation(Relevance_Score DESC);
CREATE INDEX IX_StudyRecommendation_Generated ON StudyRecommendation(Generated_At DESC);

-- ============================================================================
-- Useful Views
-- ============================================================================

-- View: Active Study Plans with Statistics
CREATE VIEW vw_ActiveStudyPlans AS
SELECT 
    sp.Plan_ID,
    sp.Student_ID,
    sp.Course_ID,
    sp.Plan_Name,
    sp.Start_Date,
    sp.End_Date,
    sp.Status,
    sp.Completion_Percentage,
    sp.Created_At,
    COUNT(st.Task_ID) AS Total_Tasks,
    SUM(CASE WHEN st.Status = 'completed' THEN 1 ELSE 0 END) AS Completed_Tasks,
    SUM(CASE WHEN st.Status = 'pending' THEN 1 ELSE 0 END) AS Pending_Tasks,
    SUM(CASE WHEN st.Status = 'in_progress' THEN 1 ELSE 0 END) AS InProgress_Tasks,
    SUM(st.Estimated_Hours) AS Total_Estimated_Hours,
    SUM(st.Actual_Hours) AS Total_Actual_Hours
FROM StudyPlan sp
LEFT JOIN StudyTask st ON sp.Plan_ID = st.Plan_ID
WHERE sp.Status = 'active'
GROUP BY 
    sp.Plan_ID, sp.Student_ID, sp.Course_ID, sp.Plan_Name, 
    sp.Start_Date, sp.End_Date, sp.Status, sp.Completion_Percentage, sp.Created_At;

-- View: Upcoming Tasks (Due within 7 days)
CREATE VIEW vw_UpcomingTasks AS
SELECT 
    st.Task_ID,
    st.Plan_ID,
    sp.Plan_Name,
    sp.Student_ID,
    st.Task_Title,
    st.Description,
    st.Estimated_Hours,
    st.Due_Date,
    st.Priority,
    st.Status,
    DATEDIFF(day, GETDATE(), st.Due_Date) AS Days_Until_Due
FROM StudyTask st
JOIN StudyPlan sp ON st.Plan_ID = sp.Plan_ID
WHERE st.Due_Date IS NOT NULL
    AND st.Due_Date >= GETDATE()
    AND st.Due_Date <= DATEADD(day, 7, GETDATE())
    AND st.Status IN ('pending', 'in_progress')
    AND sp.Status = 'active';

-- View: Student Study Analytics
CREATE VIEW vw_StudentStudyAnalytics AS
SELECT 
    s.Student_ID,
    COUNT(DISTINCT sp.Plan_ID) AS Total_Plans,
    SUM(CASE WHEN sp.Status = 'active' THEN 1 ELSE 0 END) AS Active_Plans,
    SUM(CASE WHEN sp.Status = 'completed' THEN 1 ELSE 0 END) AS Completed_Plans,
    COUNT(st.Task_ID) AS Total_Tasks,
    SUM(CASE WHEN st.Status = 'completed' THEN 1 ELSE 0 END) AS Completed_Tasks,
    AVG(sp.Completion_Percentage) AS Avg_Completion_Rate,
    SUM(st.Estimated_Hours) AS Total_Estimated_Hours,
    SUM(st.Actual_Hours) AS Total_Actual_Hours,
    CASE 
        WHEN SUM(st.Estimated_Hours) > 0 
        THEN (SUM(st.Actual_Hours) / SUM(st.Estimated_Hours)) * 100 
        ELSE 0 
    END AS Time_Estimation_Accuracy
FROM Student s
LEFT JOIN StudyPlan sp ON s.Student_ID = sp.Student_ID
LEFT JOIN StudyTask st ON sp.Plan_ID = st.Plan_ID
GROUP BY s.Student_ID;

-- ============================================================================
-- Stored Procedures
-- ============================================================================

-- Procedure: Update Study Plan Completion Percentage
GO
CREATE PROCEDURE sp_UpdatePlanCompletion
    @Plan_ID INT
AS
BEGIN
    DECLARE @TotalTasks INT;
    DECLARE @CompletedTasks INT;
    DECLARE @CompletionPercentage DECIMAL(5,2);
    
    -- Count total and completed tasks
    SELECT 
        @TotalTasks = COUNT(*),
        @CompletedTasks = SUM(CASE WHEN Status = 'completed' THEN 1 ELSE 0 END)
    FROM StudyTask
    WHERE Plan_ID = @Plan_ID;
    
    -- Calculate percentage
    IF @TotalTasks > 0
        SET @CompletionPercentage = (@CompletedTasks * 100.0) / @TotalTasks;
    ELSE
        SET @CompletionPercentage = 0;
    
    -- Update the plan
    UPDATE StudyPlan
    SET Completion_Percentage = @CompletionPercentage
    WHERE Plan_ID = @Plan_ID;
    
    -- Auto-complete plan if 100%
    IF @CompletionPercentage = 100
    BEGIN
        UPDATE StudyPlan
        SET Status = 'completed'
        WHERE Plan_ID = @Plan_ID AND Status = 'active';
    END
END;
GO

-- Procedure: Get Student Productivity Patterns
GO
CREATE PROCEDURE sp_GetProductivityPatterns
    @Student_ID INT
AS
BEGIN
    -- Analyze focus sessions by hour of day
    SELECT 
        DATEPART(HOUR, Start_Time) AS Hour_Of_Day,
        COUNT(*) AS Session_Count,
        SUM(CASE WHEN Completed = 1 THEN 1 ELSE 0 END) AS Completed_Sessions,
        AVG(Duration) AS Avg_Duration,
        CAST(SUM(CASE WHEN Completed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(5,2)) AS Completion_Rate
    FROM Focus_Session
    WHERE Student_ID = @Student_ID
        AND Start_Time IS NOT NULL
    GROUP BY DATEPART(HOUR, Start_Time)
    ORDER BY Completion_Rate DESC;
END;
GO

-- Procedure: Archive Old Completed Plans
GO
CREATE PROCEDURE sp_ArchiveOldPlans
    @DaysOld INT = 90
AS
BEGIN
    UPDATE StudyPlan
    SET Status = 'archived'
    WHERE Status = 'completed'
        AND End_Date < DATEADD(day, -@DaysOld, GETDATE());
    
    SELECT @@ROWCOUNT AS Plans_Archived;
END;
GO

-- Procedure: Get Overdue Tasks
GO
CREATE PROCEDURE sp_GetOverdueTasks
    @Student_ID INT
AS
BEGIN
    SELECT 
        st.Task_ID,
        st.Plan_ID,
        sp.Plan_Name,
        st.Task_Title,
        st.Due_Date,
        st.Priority,
        st.Estimated_Hours,
        DATEDIFF(day, st.Due_Date, GETDATE()) AS Days_Overdue
    FROM StudyTask st
    JOIN StudyPlan sp ON st.Plan_ID = sp.Plan_ID
    WHERE sp.Student_ID = @Student_ID
        AND st.Due_Date < GETDATE()
        AND st.Status IN ('pending', 'in_progress')
        AND sp.Status = 'active'
    ORDER BY st.Due_Date ASC;
END;
GO

-- ============================================================================
-- Triggers
-- ============================================================================

-- Trigger: Auto-update plan completion when task status changes
GO
CREATE TRIGGER trg_UpdatePlanCompletion
ON StudyTask
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Update completion for affected plans
    DECLARE @Plan_ID INT;
    
    -- Handle INSERT and UPDATE
    IF EXISTS (SELECT * FROM inserted)
    BEGIN
        SELECT DISTINCT @Plan_ID = Plan_ID FROM inserted;
        EXEC sp_UpdatePlanCompletion @Plan_ID;
    END
    
    -- Handle DELETE
    IF EXISTS (SELECT * FROM deleted) AND NOT EXISTS (SELECT * FROM inserted)
    BEGIN
        SELECT DISTINCT @Plan_ID = Plan_ID FROM deleted;
        EXEC sp_UpdatePlanCompletion @Plan_ID;
    END
END;
GO

-- ============================================================================
-- Sample Data (Optional - for testing)
-- ============================================================================

-- Insert sample study plan
-- INSERT INTO StudyPlan (Student_ID, Course_ID, Plan_Name, Start_Date, End_Date, Status)
-- VALUES (1, 1, 'Midterm Preparation - Data Structures', '2025-01-01', '2025-01-31', 'active');

-- Insert sample tasks
-- INSERT INTO StudyTask (Plan_ID, Task_Title, Description, Estimated_Hours, Due_Date, Priority, Status)
-- VALUES 
-- (1, 'Review Binary Trees', 'Study chapter 5 and complete practice problems', 3.0, '2025-01-10 18:00:00', 'high', 'pending'),
-- (1, 'Practice Sorting Algorithms', 'Implement quicksort and mergesort', 4.0, '2025-01-15 18:00:00', 'medium', 'pending');

-- Insert sample recommendations
-- INSERT INTO StudyRecommendation (Student_ID, Course_ID, Topic, Resource_Type, Resource_Link, Reason, Relevance_Score)
-- VALUES 
-- (1, 1, 'Binary Trees', 'video', '/resources/videos/binary-trees', 'Based on your upcoming task', 0.95),
-- (1, 1, 'Sorting Algorithms', 'practice', '/resources/practice/sorting', 'Recommended for exam preparation', 0.88);

PRINT 'Study Plan Generator schema created successfully!';
