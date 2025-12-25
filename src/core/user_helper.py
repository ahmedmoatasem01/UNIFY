"""
Helper function to get user data for templates
"""
from repositories.repository_factory import RepositoryFactory


def get_user_data(user_id):
    """
    Get user data for display in templates
    
    Args:
        user_id: The user ID from session
        
    Returns:
        dict: User data with name, email, role, department, avatar_letter
    """
    if not user_id:
        return {
            'name': 'User',
            'email': '',
            'role': 'User',
            'department': 'Zewail City',
            'avatar_letter': 'U'
        }
    
    user_repo = RepositoryFactory.get_repository("user")
    user = user_repo.get_by_id(user_id)
    
    if not user:
        return {
            'name': 'User',
            'email': '',
            'role': 'User',
            'department': 'Zewail City',
            'avatar_letter': 'U'
        }
    
    # Get student data if user is a student
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    # Get instructor data if user is an instructor
    instructor_repo = RepositoryFactory.get_repository("instructor")
    instructor = instructor_repo.get_by_user_id(user_id)
    
    # Get TA data if user is a TA
    ta_repo = RepositoryFactory.get_repository("teaching_assistant")
    ta = ta_repo.get_by_user_id(user_id) if ta_repo else None
    
    # Determine role and get major/department
    if student:
        role = 'Student'
        department = student.Department if student.Department else 'Zewail City'
        major = student.Department if student.Department else 'Computer Science'  # Use Department as Major
        avatar_letter = 'S'  # S for Student
    elif instructor:
        role = 'Instructor'
        department = instructor.Department if instructor.Department else 'Zewail City'
        major = instructor.Department if instructor.Department else 'Computer Science'  # Use Department as Major
        avatar_letter = 'I'  # I for Instructor
    elif ta:
        role = 'TA'
        department = 'Zewail City'
        major = 'Computer Science'
        avatar_letter = 'T'  # T for TA
    else:
        role = 'User'
        department = 'Zewail City'
        major = 'Computer Science'
        avatar_letter = 'U'  # U for User
    
    return {
        'name': user.Username if user.Username else 'User',
        'email': user.Email if user.Email else '',
        'role': role,
        'department': department,
        'major': major,
        'avatar_letter': avatar_letter
    }


