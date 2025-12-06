"""
Add Student record to existing test user
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.repository_factory import RepositoryFactory
from models.student import Student

def add_student_record():
    """Add student record to test user"""
    user_repo = RepositoryFactory.get_repository("user")
    student_repo = RepositoryFactory.get_repository("student")
    
    # Get test user
    test_email = "test@zewailcity.edu.eg"
    user = user_repo.get_by_email(test_email)
    
    if not user:
        print(f"User with email {test_email} not found!")
        return
    
    # Check if student record already exists
    existing_student = student_repo.get_by_user_id(user.User_ID)
    if existing_student:
        print(f"Student record already exists for user {user.Username}!")
        print(f"  Student ID: {existing_student.Student_ID}")
        print(f"  Department: {existing_student.Department}")
        return
    
    # Create student record
    print(f"Creating student record for {user.Username}...")
    student = Student(
        User_ID=user.User_ID,
        Department="Computer Science",
        Year_Level=3,
        GPA=3.5
    )
    
    created_student = student_repo.create(student)
    print(f"[OK] Student record created!")
    print(f"  Student ID: {created_student.Student_ID}")
    print(f"  Department: {created_student.Department}")
    print(f"  Year Level: {created_student.Year_Level}")
    print(f"  GPA: {created_student.GPA}")

if __name__ == "__main__":
    try:
        add_student_record()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()