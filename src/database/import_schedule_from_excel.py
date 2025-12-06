"""
Import Schedule Data from Excel to Database
Run this script to import course schedule data from Excel file to SQL Server
"""
import os
import sys
import pandas as pd
from datetime import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_singleton import DatabaseConnection
from repositories.repository_factory import RepositoryFactory

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEDULE_PATH = os.path.join(BASE_DIR, "data", "Schedule 2025.xlsx")


def detect_time_value(val) -> str:
    """Convert time value to 'HH:MM' string"""
    if isinstance(val, pd.Timestamp):
        return val.strftime("%H:%M")
    if isinstance(val, time):
        return val.strftime("%H:%M")
    s = str(val)
    if len(s) >= 5 and s[2] == ":":
        return s[:5]
    return s


def load_and_filter_schedule():
    """Load Excel and filter for Spring 2025"""
    if not os.path.exists(SCHEDULE_PATH):
        print(f"Error: Excel file not found at {SCHEDULE_PATH}")
        return None
    
    df = pd.read_excel(SCHEDULE_PATH)
    
    # Filter by year/term if columns exist
    if "ACADEMIC_YEAR" in df.columns:
        df = df[df["ACADEMIC_YEAR"] == 2025]
    if "TERM" in df.columns:
        df["TERM"] = df["TERM"].astype(str).str.upper()
        df = df[df["TERM"].str.contains("SPRG", na=False)]
    
    return df


def get_or_create_default_instructor():
    """Get or create a default instructor for courses"""
    from repositories.repository_factory import RepositoryFactory
    instructor_repo = RepositoryFactory.get_repository("instructor")
    user_repo = RepositoryFactory.get_repository("user")
    
    # Check if default instructor exists
    instructors = instructor_repo.get_all()
    if instructors:
        return instructors[0]
    
    # Create a default user for instructor
    from models.user import User
    import hashlib
    default_user = User(
        Username="Default Instructor",
        Email="instructor@zewailcity.edu.eg",
        Password_Hash=hashlib.sha256("default".encode()).hexdigest()
    )
    user = user_repo.create(default_user)
    
    # Create default instructor
    from models.instructor import Instructor
    instructor = Instructor(
        User_ID=user.User_ID,
        Department="General",
        Office="TBD",
        Email="instructor@zewailcity.edu.eg"
    )
    return instructor_repo.create(instructor)


def get_or_create_course(course_code, course_name, course_repo):
    """Get existing course or create new one"""
    # Try to find by name first
    courses = course_repo.get_all()
    for course in courses:
        if course.Course_Name == course_code or course.Course_Name == course_name:
            return course
    
    # Get or create default instructor
    default_instructor = get_or_create_default_instructor()
    
    # Create new course
    from models.course import Course
    new_course = Course(
        Course_Name=course_code,
        Credits=3,  # Default, adjust as needed
        Instructor_ID=default_instructor.Instructor_ID,
        Schedule=None
    )
    return course_repo.create(new_course)


def import_schedule_data():
    """Import schedule data from Excel to database"""
    print("Loading Excel file...")
    df = load_and_filter_schedule()
    
    if df is None or df.empty:
        print("No data to import")
        return
    
    print(f"Found {len(df)} rows to import")
    
    # Get repositories
    course_repo = RepositoryFactory.get_repository("course")
    slot_repo = RepositoryFactory.get_repository("course_schedule_slot")
    
    # Column mappings (adjust based on your Excel structure)
    COURSE_CODE_COL = "EVENT_ID"
    SECTION_COL = "SECTION"
    DAY_COL = "DAY"
    SUBTYPE_COL = "EVENT_SUB_TYPE"
    START_COL = "START_TIME"  # Adjust column names as needed
    END_COL = "END_TIME"
    TITLE_COL = "CRSE_TITLE"
    
    # Check which columns exist
    available_cols = df.columns.tolist()
    print(f"Available columns: {available_cols}")
    
    # Find actual column names (case-insensitive)
    def find_col(possible_names):
        for name in possible_names:
            for col in available_cols:
                if col.upper() == name.upper():
                    return col
        return None
    
    course_code_col = find_col(["EVENT_ID", "COURSE_CODE", "CODE"])
    section_col = find_col(["SECTION", "SEC"])
    day_col = find_col(["DAY", "WEEKDAY"])
    subtype_col = find_col(["EVENT_SUB_TYPE", "SUB_TYPE", "TYPE"])
    start_col = find_col(["START_TIME", "START", "START_STR"])
    end_col = find_col(["END_TIME", "END", "END_STR"])
    title_col = find_col(["CRSE_TITLE", "COURSE_TITLE", "TITLE", "COURSE_NAME"])
    
    if not course_code_col:
        print("Error: Could not find course code column")
        return
    
    slots_to_create = []
    courses_created = 0
    slots_created = 0
    
    print("\nProcessing rows...")
    for idx, row in df.iterrows():
        try:
            course_code = str(row[course_code_col]).strip()
            if not course_code or course_code == 'nan':
                continue
            
            course_name = str(row[title_col]).strip() if title_col else course_code
            section = int(row[section_col]) if section_col and pd.notna(row.get(section_col)) else 1
            day = str(row[day_col]).strip().upper() if day_col and pd.notna(row.get(day_col)) else "SUN"
            start_time = detect_time_value(row[start_col]) if start_col and pd.notna(row.get(start_col)) else "08:00"
            end_time = detect_time_value(row[end_col]) if end_col and pd.notna(row.get(end_col)) else "09:00"
            subtype = str(row[subtype_col]).strip().upper() if subtype_col and pd.notna(row.get(subtype_col)) else "LCTR"
            
            # Determine slot type
            if subtype == "LCTR":
                slot_type = "lecture"
            elif subtype in ["LAB", "TUTR"]:
                slot_type = "lab" if subtype == "LAB" else "tutorial"
            else:
                slot_type = "lecture"
            
            # Get or create course
            course = get_or_create_course(course_code, course_name, course_repo)
            if not course:
                print(f"Warning: Could not create/find course {course_code}")
                continue
            
            slots_to_create.append({
                'Course_ID': course.Course_ID,
                'Course_Code': course_code,
                'Section': section,
                'Day': day,
                'Start_Time': start_time,
                'End_Time': end_time,
                'Slot_Type': slot_type,
                'Sub_Type': subtype,
                'Academic_Year': 2025,
                'Term': 'SPRING'
            })
            
            if len(slots_to_create) >= 100:  # Batch insert
                slot_repo.create_batch(slots_to_create)
                slots_created += len(slots_to_create)
                slots_to_create = []
                print(f"Imported {slots_created} slots...")
        
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            continue
    
    # Insert remaining slots
    if slots_to_create:
        slot_repo.create_batch(slots_to_create)
        slots_created += len(slots_to_create)
    
    print(f"\nImport complete!")
    print(f"Total slots imported: {slots_created}")


if __name__ == "__main__":
    print("=" * 50)
    print("Course Schedule Import Tool")
    print("=" * 50)
    import_schedule_data()

