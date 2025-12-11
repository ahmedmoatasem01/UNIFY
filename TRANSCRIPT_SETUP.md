# Transcript Feature Setup Guide

This guide explains the changes made to implement the Transcript feature and how to set it up.

## Changes Made

### 1. Database Schema Updates
- **Added Grade and Semester columns to Enrollment table**
  - `Grade VARCHAR(5)` - Stores letter grades (A, A-, B+, etc.)
  - `Semester VARCHAR(50)` - Stores semester names (e.g., "Fall 2023", "Spring 2024")

### 2. Model Updates
- Updated `Enrollment` model (`src/models/enrollment.py`) to include Grade and Semester fields

### 3. Repository Updates
- Updated `EnrollmentRepository` (`src/repositories/enrollment.repository.py`) to handle Grade and Semester fields in all CRUD operations

### 4. New Controller
- Created `transcript_controller.py` with API endpoints:
  - `GET /transcript/` - Render transcript page
  - `GET /transcript/api/data` - Get transcript data for current user

### 5. Frontend
- Complete Transcript.html with:
  - Summary cards (GPA, Credits, Semesters, Dean's List)
  - Grade distribution chart
  - Semester tabs with course details
  - Complete transcript table
  - Search and filter functionality
  - Print/Download options

## Setup Instructions

### Step 1: Run Database Migration

You need to add the Grade and Semester columns to your existing Enrollment table.

**For MySQL:**
```sql
USE unify;

ALTER TABLE Enrollment 
ADD COLUMN Grade VARCHAR(5) DEFAULT NULL;

ALTER TABLE Enrollment 
ADD COLUMN Semester VARCHAR(50) DEFAULT NULL;
```

**Or run the migration script:**
```bash
mysql -u your_username -p unify < src/database/migrations/add_grade_semester_to_enrollment.sql
```

### Step 2: Populate Sample Data (Optional for Testing)

To test the transcript feature, you can add some sample enrollment data with grades:

```sql
-- Example: Add sample grades to existing enrollments
UPDATE Enrollment 
SET Grade = 'A', Semester = 'Fall 2023'
WHERE Enrollment_ID = 1;

UPDATE Enrollment 
SET Grade = 'B+', Semester = 'Fall 2023'
WHERE Enrollment_ID = 2;

-- Or insert new enrollments with grades
INSERT INTO Enrollment (Student_ID, Course_ID, Status, Grade, Semester)
VALUES 
  (1, 1, 'completed', 'A', 'Fall 2023'),
  (1, 2, 'completed', 'A-', 'Fall 2023'),
  (1, 3, 'completed', 'B+', 'Spring 2024');
```

### Step 3: Restart the Application

The Flask application should automatically pick up the new controller. If you're running the app:

```bash
# Make sure you're in the UNIFY directory
cd UNIFY/src
python app.py
```

### Step 4: Access the Transcript Page

Navigate to: `http://localhost:5000/transcript`

## Features

### Summary Cards
- **Cumulative GPA**: Calculated from all completed courses
- **Total Credits**: Sum of all completed course credits
- **Semesters**: Number of distinct semesters
- **Dean's List**: Count of semesters with GPA ≥ 3.7

### Grade Distribution Chart
- Visual pie chart showing distribution of grades (A, B, C, D, F)

### Semester Details
- Tab interface to view courses by semester
- Each semester shows:
  - Semester GPA
  - Credits taken
  - Course cards with grades

### Complete Transcript Table
- Searchable and filterable table
- Filters by:
  - Course code/name (search)
  - Semester (dropdown)
  - Grade level (dropdown)

### Actions
- **Print**: Print-friendly transcript view
- **Download**: PDF download (placeholder for future implementation)

## API Endpoint Details

### GET /transcript/api/data

Returns transcript data for the authenticated user.

**Response Format:**
```json
{
  "student": {
    "name": "Student Name",
    "id": "123",
    "program": "Computer Science",
    "email": "student@example.com",
    "avatar": "S"
  },
  "summary": {
    "cumulativeGPA": 3.75,
    "totalCredits": 45,
    "academicStanding": "Good",
    "deansListCount": 2
  },
  "semesters": [
    {
      "id": "fall-2023",
      "name": "Fall 2023",
      "gpa": 3.8,
      "credits": 15,
      "courses": [
        {
          "code": "COURSE1",
          "name": "Introduction to Programming",
          "credits": 3,
          "grade": "A",
          "gradePoint": 4.0,
          "semester": "Fall 2023",
          "semesterId": "fall-2023"
        }
      ]
    }
  ]
}
```

## Grade Point Scale

The system uses the following grade point scale:

| Grade | Points |
|-------|--------|
| A+, A | 4.0    |
| A-    | 3.7    |
| B+    | 3.3    |
| B     | 3.0    |
| B-    | 2.7    |
| C+    | 2.3    |
| C     | 2.0    |
| C-    | 1.7    |
| D+    | 1.3    |
| D     | 1.0    |
| D-    | 0.7    |
| F     | 0.0    |

## Troubleshooting

### "Not authenticated" Error
- Make sure you're logged in
- Check that the session is active

### No courses showing
- Verify that you have enrollments with Status = 'completed'
- Make sure Grade and Semester fields are populated
- Check that the enrollments are linked to valid courses

### Database connection errors
- Verify database credentials in your configuration
- Ensure the database is running
- Check that migrations have been applied

## Future Enhancements

Possible improvements:
1. PDF generation for transcript download
2. Email transcript functionality
3. Course prerequisites and requirements tracking
4. Academic progress towards degree completion
5. Comparative analytics (class average, percentile)
6. Semester registration history
7. Transfer credit management

