# Import Courses from Schedule 2025.xlsx to Database

## Problem
The Course Registration page shows no courses because the `Course_Schedule_Slot` table is empty.

## Solution
Import the Excel data into your database using the provided script.

## Step-by-Step Instructions

### Step 1: Make Sure You Have the Required Table

Run this in SSMS to create the Course_Schedule_Slot table (if it doesn't exist):

```sql
USE unify;
GO

-- Check if table exists
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Course_Schedule_Slot')
BEGIN
    CREATE TABLE Course_Schedule_Slot (
        Slot_ID INT IDENTITY(1,1) PRIMARY KEY,
        Course_ID INT NOT NULL,
        Course_Code VARCHAR(50) NOT NULL,
        Section INT NOT NULL,
        Day VARCHAR(10) NOT NULL,
        Start_Time TIME NOT NULL,
        End_Time TIME NOT NULL,
        Slot_Type VARCHAR(20) NOT NULL,
        Sub_Type VARCHAR(10),
        Academic_Year INT,
        Term VARCHAR(20),
        CONSTRAINT FK_Slot_Course FOREIGN KEY (Course_ID)
            REFERENCES Course(Course_ID) ON DELETE CASCADE
    );

    CREATE INDEX idx_course_code ON Course_Schedule_Slot(Course_Code);
    CREATE INDEX idx_course_id ON Course_Schedule_Slot(Course_ID);
    CREATE INDEX idx_day_time ON Course_Schedule_Slot(Day, Start_Time);
    
    PRINT 'Course_Schedule_Slot table created successfully!';
END
ELSE
BEGIN
    PRINT 'Course_Schedule_Slot table already exists.';
END
GO
```

### Step 2: Run the Import Script

Open PowerShell and run:

```powershell
cd C:\Users\Acer\Desktop\Unify\UNIFY\src
python database/import_schedule_from_excel.py
```

This will:
- ✅ Read `data/Schedule 2025.xlsx`
- ✅ Extract all 292 courses
- ✅ Create Course records in the Course table
- ✅ Create schedule slots in Course_Schedule_Slot table
- ✅ Handle lectures, labs, and tutorials

### Step 3: Verify Import

Run this in SSMS:

```sql
USE unify;
GO

-- Check how many courses were imported
SELECT COUNT(*) as Total_Courses FROM Course;

-- Check how many schedule slots were imported
SELECT COUNT(*) as Total_Slots FROM Course_Schedule_Slot;

-- Show sample courses
SELECT TOP 10 Course_ID, Course_Name, Credits FROM Course ORDER BY Course_Name;

-- Show sample schedule slots
SELECT TOP 10 
    Course_Code, 
    Section, 
    Day, 
    Start_Time, 
    End_Time, 
    Slot_Type 
FROM Course_Schedule_Slot 
ORDER BY Course_Code, Section, Day;
GO
```

You should see:
- ✅ 292 courses in Course table
- ✅ Hundreds of slots in Course_Schedule_Slot table

### Step 4: Test Course Registration

1. Go to: `http://localhost:5000/course-registration`
2. Type a course code like: `CSAI 101` or `MATH 101`
3. Click Search
4. You should see courses with available lecture/lab sections!

## How It Works

### Data Flow:
```
Schedule 2025.xlsx 
    ↓ (one-time import)
Course table + Course_Schedule_Slot table
    ↓ (reading)
Course Registration page
    ↓ (user registers)
Enrollment table (with Status='enrolled')
```

### When User Registers:
1. User searches courses
2. Adds to cart
3. Clicks "Optimize Schedule"
4. System finds best sections with no conflicts
5. User clicks "Enroll"
6. Creates Enrollment records in database
7. Data is permanently saved!

## Advantages of Database Storage

✅ **Fast** - No Excel file reading on every request
✅ **Reliable** - Data persists, no file dependencies
✅ **Queryable** - Can filter, search, join with other tables
✅ **Scalable** - Can handle thousands of courses
✅ **Updatable** - Can modify courses without touching Excel

## Alternative: Manual SQL Import (if Python import fails)

If the Python script doesn't work, I can generate a SQL script to insert all 292 courses directly. Let me know if you need that!

