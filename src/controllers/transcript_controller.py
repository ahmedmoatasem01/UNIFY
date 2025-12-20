from flask import Blueprint, render_template, request, jsonify, session
from repositories.repository_factory import RepositoryFactory

transcript_bp = Blueprint("transcript", __name__, url_prefix="/transcript")


@transcript_bp.route("/", methods=["GET"])
def transcript_page():
    """Render the transcript page"""
    return render_template("Transcript.html")


@transcript_bp.route("/api/data", methods=["GET"])
def api_get_transcript_data():
    """API endpoint to get transcript data for the current user"""
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
    
    # Group enrollments by semester
    semesters_dict = {}
    all_courses = []
    total_credits = 0
    total_grade_points = 0
    
    for enrollment in enrollments:
        # Only include completed courses with grades
        if enrollment.Status != 'completed' or not enrollment.Grade or not enrollment.Semester:
            continue
        
        course = course_repo.get_by_id(enrollment.Course_ID)
        if not course:
            continue
        
        grade_point = grade_points.get(enrollment.Grade, 0.0)
        
        course_data = {
            'code': f'COURSE{course.Course_ID}',  # You can customize this
            'name': course.Course_Name,
            'credits': course.Credits,
            'grade': enrollment.Grade,
            'gradePoint': grade_point,
            'semester': enrollment.Semester,
            'semesterId': enrollment.Semester.lower().replace(' ', '-')
        }
        
        all_courses.append(course_data)
        
        # Calculate totals
        total_credits += course.Credits
        total_grade_points += grade_point * course.Credits
        
        # Group by semester
        if enrollment.Semester not in semesters_dict:
            semesters_dict[enrollment.Semester] = {
                'id': enrollment.Semester.lower().replace(' ', '-'),
                'name': enrollment.Semester,
                'courses': [],
                'credits': 0,
                'grade_points': 0
            }
        
        semesters_dict[enrollment.Semester]['courses'].append(course_data)
        semesters_dict[enrollment.Semester]['credits'] += course.Credits
        semesters_dict[enrollment.Semester]['grade_points'] += grade_point * course.Credits
    
    # Calculate cumulative GPA
    cumulative_gpa = total_grade_points / total_credits if total_credits > 0 else 0.0
    
    # Calculate semester GPAs and format semester data
    semesters = []
    deans_list_count = 0
    
    for semester_name, semester_data in semesters_dict.items():
        semester_credits = semester_data['credits']
        semester_grade_points = semester_data['grade_points']
        semester_gpa = semester_grade_points / semester_credits if semester_credits > 0 else 0.0
        
        if semester_gpa >= 3.7:
            deans_list_count += 1
        
        semesters.append({
            'id': semester_data['id'],
            'name': semester_data['name'],
            'gpa': round(semester_gpa, 2),
            'credits': semester_credits,
            'courses': semester_data['courses']
        })
    
    # Sort semesters (you might want to customize this based on your semester naming)
    semesters.sort(key=lambda x: x['name'])
    
    # Determine academic standing
    if cumulative_gpa >= 3.5:
        academic_standing = 'Good'
    elif cumulative_gpa >= 2.0:
        academic_standing = 'Satisfactory'
    else:
        academic_standing = 'Warning'
    
    # Build response
    transcript_data = {
        'student': {
            'name': user.Username if user else 'Student',
            'id': str(student.Student_ID),
            'program': student.Department or 'Computer Science',
            'email': user.Email if user else '',
            'avatar': user.Username[0].upper() if user and user.Username else 'S'
        },
        'summary': {
            'cumulativeGPA': round(cumulative_gpa, 2),
            'totalCredits': total_credits,
            'academicStanding': academic_standing,
            'deansListCount': deans_list_count
        },
        'semesters': semesters
    }
    
    return jsonify(transcript_data)


@transcript_bp.route("/api/print", methods=["GET"])
def api_generate_pdf():
    """API endpoint to generate PDF transcript (placeholder)"""
    return jsonify({"message": "PDF generation not yet implemented"}), 501

