"""
Seed Cohort Data for Academic Dashboard (FR16)
Creates multiple students in the same batch with grades for comparison
"""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.repository_factory import RepositoryFactory
from models.student import Student
from models.enrollment import Enrollment
from models.user import User
import hashlib

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def seed_cohort_data():
    """Create cohort of students with grades for comparison"""
    print("=" * 60)
    print("Cohort Data Seeding Script (FR16)")
    print("=" * 60)
    print("\nCreating students in the same batch with grades...\n")

    try:
        user_repo = RepositoryFactory.get_repository('user')
        student_repo = RepositoryFactory.get_repository('student')
        enrollment_repo = RepositoryFactory.get_repository('enrollment')
        course_repo = RepositoryFactory.get_repository('course')

        if not all([user_repo, student_repo, enrollment_repo, course_repo]):
            print("[ERROR] One or more repositories not available.")
            return

        # Get some courses to enroll students in
        all_courses = course_repo.get_all()
        if not all_courses:
            print("[ERROR] No courses found. Please import courses first.")
            return

        # Use first 10 courses
        courses_to_use = all_courses[:10]

        # Define cohort: Same department and year level
        department = "Computer Science & AI"
        year_level = 3

        # Create 10 students in the same cohort with varying GPAs
        cohort_students = []
        student_data = [
            {"username": "ahmed_hasan", "email": "ahmed.hasan@student.zewailcity.edu.eg", "gpa_range": (3.5, 3.8)},
            {"username": "sara_mohamed", "email": "sara.mohamed@student.zewailcity.edu.eg", "gpa_range": (3.2, 3.5)},
            {"username": "omar_ali", "email": "omar.ali@student.zewailcity.edu.eg", "gpa_range": (3.7, 4.0)},
            {"username": "fatima_ibrahim", "email": "fatima.ibrahim@student.zewailcity.edu.eg", "gpa_range": (2.8, 3.2)},
            {"username": "youssef_ahmed", "email": "youssef.ahmed@student.zewailcity.edu.eg", "gpa_range": (3.0, 3.4)},
            {"username": "nour_hassan", "email": "nour.hassan@student.zewailcity.edu.eg", "gpa_range": (3.6, 3.9)},
            {"username": "mohamed_khalil", "email": "mohamed.khalil@student.zewailcity.edu.eg", "gpa_range": (2.5, 2.9)},
            {"username": "laila_said", "email": "laila.said@student.zewailcity.edu.eg", "gpa_range": (3.4, 3.7)},
            {"username": "karim_farid", "email": "karim.farid@student.zewailcity.edu.eg", "gpa_range": (3.1, 3.5)},
            {"username": "dina_mostafa", "email": "dina.mostafa@student.zewailcity.edu.eg", "gpa_range": (3.3, 3.6)},
        ]

        # Grade distribution based on GPA range
        grade_mapping = {
            (3.7, 4.0): ['A', 'A-', 'A+', 'A', 'B+'],
            (3.5, 3.7): ['A-', 'B+', 'A', 'B+', 'B'],
            (3.2, 3.5): ['B+', 'B', 'B', 'B-', 'B+'],
            (3.0, 3.2): ['B', 'B-', 'B', 'C+', 'B-'],
            (2.8, 3.0): ['B-', 'C+', 'B-', 'C', 'C+'],
            (2.5, 2.8): ['C+', 'C', 'C', 'C-', 'C'],
        }

        semesters = ['Fall 2022', 'Spring 2023', 'Fall 2023', 'Spring 2024', 'Fall 2024']

        for idx, student_info in enumerate(student_data):
            username = student_info["username"]
            email = student_info["email"]
            gpa_range = student_info["gpa_range"]

            # Check if user already exists
            existing_user = user_repo.get_by_email(email)
            if existing_user:
                user = existing_user
                print(f"[SKIP] User {username} already exists")
            else:
                # Create user
                user = User(
                    Username=username,
                    Email=email,
                    Password_Hash=hash_password("password123")
                )
                user = user_repo.create(user)
                print(f"[OK] Created user: {username}")

            # Check if student already exists
            existing_student = student_repo.get_by_user_id(user.User_ID)
            if existing_student:
                student = existing_student
                # Update to ensure correct cohort
                student.Department = department
                student.Year_Level = year_level
                student = student_repo.update(student)
                print(f"[SKIP] Student record already exists for {username}")
            else:
                # Create student
                student = Student(
                    User_ID=user.User_ID,
                    Department=department,
                    Year_Level=year_level,
                    GPA=None  # Will be calculated from enrollments
                )
                student = student_repo.create(student)
                print(f"[OK] Created student: {username} (ID: {student.Student_ID})")

            cohort_students.append((student, gpa_range))

            # Create enrollments with grades
            # Each student gets 5-8 completed courses with grades
            num_courses = 5 + (idx % 4)  # Vary between 5-8 courses
            courses_for_student = courses_to_use[:num_courses]

            # Get grade pattern for this GPA range
            grade_pattern = []
            for gpa_range_key, grades in grade_mapping.items():
                if gpa_range[0] >= gpa_range_key[0] and gpa_range[1] <= gpa_range_key[1]:
                    grade_pattern = grades
                    break
            if not grade_pattern:
                grade_pattern = ['B', 'B+', 'B', 'B-', 'C+']

            for course_idx, course in enumerate(courses_for_student):
                # Check if enrollment already exists
                existing_enrollments = enrollment_repo.get_by_student(student.Student_ID)
                existing = next((e for e in existing_enrollments if e.Course_ID == course.Course_ID), None)

                if existing:
                    # Update existing enrollment with grade
                    if not existing.Grade:
                        existing.Grade = grade_pattern[course_idx % len(grade_pattern)]
                        existing.Semester = semesters[course_idx % len(semesters)]
                        existing.Status = 'completed'
                        enrollment_repo.update(existing)
                        print(f"  [UPDATE] Added grade {existing.Grade} for {course.Course_Name}")
                    continue

                # Create new enrollment with grade
                grade = grade_pattern[course_idx % len(grade_pattern)]
                semester = semesters[course_idx % len(semesters)]

                enrollment = Enrollment(
                    Student_ID=student.Student_ID,
                    Course_ID=course.Course_ID,
                    Status='completed',
                    Grade=grade,
                    Semester=semester
                )
                enrollment_repo.create(enrollment)
                print(f"  [OK] Enrolled in {course.Course_Name} - Grade: {grade}, Semester: {semester}")

        print(f"\n[SUCCESS] Created cohort of {len(cohort_students)} students!")
        print(f"  Department: {department}")
        print(f"  Year Level: {year_level}")
        print(f"\n[INFO] All students have password: password123")
        print(f"[INFO] Login with any student account to see cohort comparison in Overview page")

    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "=" * 60)
        print("Done! Check the Overview page to see the academic dashboard.")
        print("=" * 60 + "\n")

if __name__ == '__main__':
    seed_cohort_data()

