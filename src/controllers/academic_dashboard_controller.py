from flask import Blueprint, render_template, request, jsonify, session, redirect
from repositories.repository_factory import RepositoryFactory
from datetime import datetime, timedelta
from core.user_helper import get_user_data

academic_dashboard_bp = Blueprint("academic_dashboard", __name__, url_prefix="/academic-dashboard")


@academic_dashboard_bp.route("/", methods=["GET"])
def academic_dashboard_page():
    """Render the academic dashboard page"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    user_data = get_user_data(user_id)
    return render_template("academic_dashboard.html", user_data=user_data)


@academic_dashboard_bp.route("/api/data", methods=["GET"])
def api_get_dashboard_data():
    """API endpoint to get comprehensive academic dashboard data"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get student information
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    # Get user information
    user_repo = RepositoryFactory.get_repository("user")
    user = user_repo.get_by_id(user_id)
    
    # Get enrollments for the student
    enrollment_repo = RepositoryFactory.get_repository("enrollment")
    enrollments = enrollment_repo.get_by_student_id(student.Student_ID)
    
    # Get course information
    course_repo = RepositoryFactory.get_repository("course")
    
    # Grade to point conversion
    grade_points = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0, 'D-': 0.7,
        'F': 0.0
    }
    
    # Calculate GPA and course data
    all_courses = []
    total_credits = 0
    total_grade_points = 0
    completed_credits = 0
    in_progress_credits = 0
    
    semester_gpas = []
    semesters_dict = {}
    
    for enrollment in enrollments:
        course = course_repo.get_by_id(enrollment.Course_ID)
        if not course:
            continue
        
        course_data = {
            'id': course.Course_ID,
            'code': f'COURSE{course.Course_ID}',
            'name': course.Course_Name,
            'credits': course.Credits,
            'semester': enrollment.Semester or 'N/A',
            'status': enrollment.Status or 'in_progress',
            'grade': enrollment.Grade,
            'gradePoint': grade_points.get(enrollment.Grade, 0.0) if enrollment.Grade else None
        }
        
        all_courses.append(course_data)
        
        # Calculate credits and GPA
        if enrollment.Status == 'completed' and enrollment.Grade:
            grade_point = grade_points.get(enrollment.Grade, 0.0)
            total_credits += course.Credits
            total_grade_points += grade_point * course.Credits
            completed_credits += course.Credits
            
            # Group by semester for semester GPA
            semester = enrollment.Semester or 'Unknown'
            if semester not in semesters_dict:
                semesters_dict[semester] = {
                    'name': semester,
                    'credits': 0,
                    'grade_points': 0,
                    'courses': []
                }
            semesters_dict[semester]['credits'] += course.Credits
            semesters_dict[semester]['grade_points'] += grade_point * course.Credits
            semesters_dict[semester]['courses'].append(course_data)
        elif enrollment.Status == 'in_progress' or enrollment.Status == 'enrolled':
            in_progress_credits += course.Credits
    
    # Calculate cumulative GPA
    cumulative_gpa = total_grade_points / total_credits if total_credits > 0 else 0.0
    
    # Calculate semester GPAs
    for semester_name, semester_data in semesters_dict.items():
        semester_credits = semester_data['credits']
        semester_grade_points = semester_data['grade_points']
        semester_gpa = semester_grade_points / semester_credits if semester_credits > 0 else 0.0
        
        semester_gpas.append({
            'semester': semester_name,
            'gpa': round(semester_gpa, 2),
            'credits': semester_credits
        })
    
    # Sort semesters
    semester_gpas.sort(key=lambda x: x['semester'])
    
    # Calculate graduation timeline prediction
    # Assume 120 credits required for graduation (typical for 4-year degree)
    required_credits = 120
    credits_remaining = max(0, required_credits - completed_credits)
    progress_percentage = (completed_credits / required_credits * 100) if required_credits > 0 else 0
    
    # Estimate graduation date
    # Assume average of 15 credits per semester (typical full-time load)
    credits_per_semester = 15
    semesters_remaining = max(1, (credits_remaining + credits_per_semester - 1) // credits_per_semester)
    
    # Estimate graduation date (assuming 2 semesters per year)
    current_date = datetime.now()
    years_remaining = semesters_remaining / 2.0
    estimated_graduation = current_date + timedelta(days=int(years_remaining * 365))
    
    # Calculate cohort performance
    cohort_gpa = calculate_cohort_gpa(student.Department, student.Year_Level, student_repo, enrollment_repo, course_repo, grade_points)
    
    # Build response
    dashboard_data = {
        'student': {
            'name': user.Username if user else 'Student',
            'id': str(student.Student_ID),
            'department': student.Department or 'Computer Science',
            'yearLevel': student.Year_Level or 1
        },
        'gpa': {
            'cumulative': round(cumulative_gpa, 2),
            'semesterGpas': semester_gpas,
            'trend': calculate_gpa_trend(semester_gpas)
        },
        'credits': {
            'completed': completed_credits,
            'inProgress': in_progress_credits,
            'remaining': credits_remaining,
            'required': required_credits,
            'progressPercentage': round(progress_percentage, 1)
        },
        'graduation': {
            'estimatedDate': estimated_graduation.strftime('%Y-%m-%d'),
            'estimatedYear': estimated_graduation.year,
            'semestersRemaining': semesters_remaining,
            'onTrack': progress_percentage >= (student.Year_Level or 1) * 25  # Should be at least 25% per year
        },
        'courses': {
            'all': all_courses,
            'completed': [c for c in all_courses if c['status'] == 'completed'],
            'inProgress': [c for c in all_courses if c['status'] in ['in_progress', 'enrolled']]
        },
        'cohort': {
            'averageGpa': round(cohort_gpa, 2) if cohort_gpa else None,
            'studentGpa': round(cumulative_gpa, 2),
            'percentile': calculate_percentile(cumulative_gpa, cohort_gpa) if cohort_gpa else None,
            'comparison': 'above' if cohort_gpa and cumulative_gpa > cohort_gpa else 'below' if cohort_gpa and cumulative_gpa < cohort_gpa else 'equal'
        }
    }
    
    return jsonify(dashboard_data)


def calculate_cohort_gpa(department, year_level, student_repo, enrollment_repo, course_repo, grade_points):
    """Calculate average GPA for students in the same department and year level"""
    try:
        # Get all students in the same department and year level
        if not department or not year_level:
            return None
        
        all_students = student_repo.get_all()
        cohort_students = [
            s for s in all_students 
            if s.Department == department and s.Year_Level == year_level
        ]
        
        if not cohort_students:
            return None
        
        cohort_gpas = []
        
        for cohort_student in cohort_students:
            enrollments = enrollment_repo.get_by_student_id(cohort_student.Student_ID)
            
            total_credits = 0
            total_grade_points = 0
            
            for enrollment in enrollments:
                if enrollment.Status == 'completed' and enrollment.Grade:
                    course = course_repo.get_by_id(enrollment.Course_ID)
                    if course:
                        grade_point = grade_points.get(enrollment.Grade, 0.0)
                        total_credits += course.Credits
                        total_grade_points += grade_point * course.Credits
            
            if total_credits > 0:
                student_gpa = total_grade_points / total_credits
                cohort_gpas.append(student_gpa)
        
        if cohort_gpas:
            return sum(cohort_gpas) / len(cohort_gpas)
        
        return None
    except Exception as e:
        print(f"Error calculating cohort GPA: {e}")
        return None


def calculate_gpa_trend(semester_gpas):
    """Calculate GPA trend (improving, declining, stable)"""
    if len(semester_gpas) < 2:
        return 'stable'
    
    recent_gpas = [s['gpa'] for s in semester_gpas[-3:]]  # Last 3 semesters
    if len(recent_gpas) < 2:
        return 'stable'
    
    # Calculate average of first half vs second half
    mid = len(recent_gpas) // 2
    first_half_avg = sum(recent_gpas[:mid]) / mid
    second_half_avg = sum(recent_gpas[mid:]) / len(recent_gpas[mid:])
    
    diff = second_half_avg - first_half_avg
    
    if diff > 0.1:
        return 'improving'
    elif diff < -0.1:
        return 'declining'
    else:
        return 'stable'


def calculate_percentile(student_gpa, cohort_avg_gpa):
    """Calculate approximate percentile (simplified)"""
    if not cohort_avg_gpa:
        return None
    
    # Simplified percentile calculation
    # If student GPA is above average, they're likely in top 50%
    # This is a simplified calculation - in reality, you'd need all cohort GPAs
    if student_gpa >= cohort_avg_gpa + 0.5:
        return 90
    elif student_gpa >= cohort_avg_gpa + 0.3:
        return 75
    elif student_gpa >= cohort_avg_gpa:
        return 60
    elif student_gpa >= cohort_avg_gpa - 0.3:
        return 40
    else:
        return 25

