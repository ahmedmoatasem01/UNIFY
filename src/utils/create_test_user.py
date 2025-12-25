"""
Create Test User Script
Run this to create a test user in the database for login testing
"""
import sys
import os
import hashlib

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_singleton import DatabaseConnection
from repositories.repository_factory import RepositoryFactory
from models.user import User
from models.student import Student

def create_test_user():
    """Create a test user for login"""
    print("=" * 50)
    print("Creating Test User")
    print("=" * 50)
    
    # Get repositories
    user_repo = RepositoryFactory.get_repository("user")
    student_repo = RepositoryFactory.get_repository("student")
    
    # Test user data
    test_email = "test@zewailcity.edu.eg"
    test_username = "Test User"
    test_password = "password123"  # Change this to a secure password
    
    # Check if user already exists
    existing_user = user_repo.get_by_email(test_email)
    if existing_user:
        print(f"User with email {test_email} already exists!")
        print(f"User ID: {existing_user.User_ID}")
        print(f"Username: {existing_user.Username}")
        return existing_user
    
    # Hash password (same as in auth_controller)
    password_hash = hashlib.sha256(test_password.encode()).hexdigest()
    
    # Create user
    print(f"\nCreating user...")
    print(f"  Email: {test_email}")
    print(f"  Username: {test_username}")
    print(f"  Password: {test_password}")
    
    new_user = User(
        Username=test_username,
        Email=test_email,
        Password_Hash=password_hash
    )
    
    created_user = user_repo.create(new_user)
    print(f"\n[OK] User created successfully!")
    print(f"  User ID: {created_user.User_ID}")
    
    # Create student record
    print(f"\nCreating student record...")
    student = Student(
        User_ID=created_user.User_ID,
        Department="Computer Science",
        Year_Level=3,
        GPA=3.5
    )
    
    created_student = student_repo.create(student)
    print(f"[OK] Student record created!")
    print(f"  Student ID: {created_student.Student_ID}")
    
    print("\n" + "=" * 50)
    print("Test User Created Successfully!")
    print("=" * 50)
    print(f"\nYou can now login with:")
    print(f"  Email: {test_email}")
    print(f"  Password: {test_password}")
    print("\nOr register a new user through the registration form.")
    
    return created_user


if __name__ == "__main__":
    try:
        create_test_user()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

