-- Course Schedule Slots Table (SQL Server)
-- This table stores individual time slots for courses (lectures, labs, tutorials)

CREATE TABLE IF NOT EXISTS Course_Schedule_Slot (
    Slot_ID INT IDENTITY(1,1) PRIMARY KEY,
    Course_ID INT NOT NULL,
    Course_Code VARCHAR(50) NOT NULL,  -- e.g., "AIE 501"
    Section INT NOT NULL,
    Day VARCHAR(10) NOT NULL,  -- SUN, MON, TUES, WED, THURS, SAT
    Start_Time TIME NOT NULL,
    End_Time TIME NOT NULL,
    Slot_Type VARCHAR(20) NOT NULL,  -- 'lecture', 'lab', 'tutorial'
    Sub_Type VARCHAR(10),  -- 'LCTR', 'LAB', 'TUTR'
    Academic_Year INT,
    Term VARCHAR(20),  -- 'SPRING', 'FALL', etc.
    CONSTRAINT FK_Slot_Course FOREIGN KEY (Course_ID)
        REFERENCES Course(Course_ID) ON DELETE CASCADE
);

CREATE INDEX idx_course_code ON Course_Schedule_Slot(Course_Code);
CREATE INDEX idx_course_id ON Course_Schedule_Slot(Course_ID);
CREATE INDEX idx_day_time ON Course_Schedule_Slot(Day, Start_Time);

