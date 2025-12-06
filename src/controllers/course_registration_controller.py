"""
Course Registration Controller
Handles course registration page and optimization API
"""
import importlib.util
import os
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from repositories.repository_factory import RepositoryFactory
from services.course_optimization_service import CourseOptimizationService
from core.user_helper import get_user_data

# Import CourseScheduleSlotRepository using importlib to handle dots in filename
_repo_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repositories')
spec = importlib.util.spec_from_file_location(
    'course_schedule_slot_repository',
    os.path.join(_repo_dir, 'course_schedule_slot.repository.py')
)
course_schedule_slot_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(course_schedule_slot_module)
CourseScheduleSlotRepository = course_schedule_slot_module.CourseScheduleSlotRepository

course_reg_bp = Blueprint("course_registration", __name__, url_prefix="/course-registration")
optimization_service = CourseOptimizationService()


@course_reg_bp.route("/")
def course_registration_page():
    """Render course registration page"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    # Get user data from database
    user_data = get_user_data(session.get('user_id'))
    return render_template('course_registration.html', user_data=user_data)


@course_reg_bp.route("/api/courses", methods=["GET"])
def api_courses():
    """
    Return all courses (or filtered by ?q=) for the search panel.
    Returns courses with their schedule slot counts.
    Fetches courses directly from Course_Schedule_Slot table.
    """
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    q = request.args.get("q", "").strip().upper()
    academic_year = request.args.get("academic_year", 2025, type=int)
    term = request.args.get("term", "SPRING", type=str)
    
    # Get schedule slot repository
    slot_repo = CourseScheduleSlotRepository()
    
    # Get all unique courses from schedule slots
    from core.db_singleton import DatabaseConnection
    db_connection = DatabaseConnection()
    conn = db_connection.get_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT DISTINCT Course_Code, Course_ID
            FROM Course_Schedule_Slot
            WHERE Academic_Year = ? AND Term = ?
        """
        cursor.execute(query, (academic_year, term))
        rows = cursor.fetchall()
        
        # Build a map of course codes
        course_codes_map = {}
        for row in rows:
            course_code = row[0]
            course_id = row[1]
            if course_code not in course_codes_map:
                course_codes_map[course_code] = course_id
    finally:
        conn.close()
    
    results = []
    for course_code, course_id in course_codes_map.items():
        # Filter by search query
        if q and q not in course_code.upper():
            continue
        
        # Get slots for this course
        slots = slot_repo.get_by_course_code(course_code, academic_year=academic_year, term=term)
        
        if not slots:
            continue
        
        # Count lectures and labs
        lectures = [s for s in slots if s.get('Slot_Type', '').lower() == 'lecture' or s.get('Sub_Type', '') == 'LCTR']
        labs = [s for s in slots if s.get('Slot_Type', '').lower() in ['lab', 'tutorial'] or s.get('Sub_Type', '') in ['LAB', 'TUTR']]
        
        # Group by section
        lecture_sections = {}
        lab_sections = {}
        for slot in lectures:
            section = slot.get('Section', 1)
            if section not in lecture_sections:
                lecture_sections[section] = []
            lecture_sections[section].append(slot)
        
        for slot in labs:
            section = slot.get('Section', 1)
            if section not in lab_sections:
                lab_sections[section] = []
            lab_sections[section].append(slot)
        
        results.append({
            "id": course_code,
            "code": course_code,
            "name": course_code,  # Using course code as name since we don't have separate name field
            "lecture_slots": [{"section": sec, "count": len(slots)} for sec, slots in lecture_sections.items()],
            "lab_slots": [{"section": sec, "count": len(slots)} for sec, slots in lab_sections.items()],
        })
    
    return jsonify(results)


@course_reg_bp.route("/api/optimize", methods=["POST"])
def api_optimize():
    """
    Optimize course schedule to find conflict-free section combinations.
    
    Request JSON:
    {
        "course_ids": ["AIE 501", "BGEN 201", ...],
        "academic_year": 2025,
        "term": "SPRING"
    }
    
    Response JSON:
    {
        "status": "ok" | "no_solution" | "error",
        "schedule": [...],
        "message": "..."
    }
    """
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json(silent=True) or {}
    course_ids = data.get("course_ids", [])
    academic_year = data.get("academic_year", 2025)
    term = data.get("term", "SPRING")
    
    if not course_ids:
        return jsonify({"status": "error", "message": "No course_ids provided.", "schedule": None}), 400
    
    result = optimization_service.optimize_schedule(course_ids, academic_year, term)
    
    if result["status"] == "error":
        return jsonify(result), 404
    elif result["status"] == "no_solution":
        return jsonify(result), 200
    
    return jsonify(result)


@course_reg_bp.route("/api/enroll", methods=["POST"])
def api_enroll():
    """
    Enroll student in optimized courses.
    
    Request JSON:
    {
        "schedule": [...],  # Optimized schedule from /api/optimize
        "student_id": int
    }
    """
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json(silent=True) or {}
    schedule = data.get("schedule", [])
    student_id = data.get("student_id")
    
    if not student_id:
        # Get student_id from session
        user_id = session.get('user_id')
        student_repo = RepositoryFactory.get_repository("student")
        student = student_repo.get_by_user_id(user_id)
        if not student:
            return jsonify({"error": "Student record not found"}), 404
        student_id = student.Student_ID
    
    if not schedule:
        return jsonify({"error": "No schedule provided"}), 400
    
    # Get unique course codes from schedule
    course_codes = list(set([slot.get("course_code") for slot in schedule]))
    
    # Get course repository
    course_repo = RepositoryFactory.get_repository("course")
    enrollment_repo = RepositoryFactory.get_repository("enrollment")
    
    enrollments = []
    errors = []
    
    for course_code in course_codes:
        # Find course by name/code (adjust based on your schema)
        courses = course_repo.get_all()
        course = None
        for c in courses:
            if c.Course_Name == course_code or str(c.Course_ID) == course_code:
                course = c
                break
        
        if not course:
            errors.append(f"Course {course_code} not found")
            continue
        
        # Check if already enrolled
        existing = enrollment_repo.get_by_student(student_id)
        already_enrolled = any(e.Course_ID == course.Course_ID for e in existing)
        
        if not already_enrolled:
            from models.enrollment import Enrollment
            enrollment = Enrollment(
                Student_ID=student_id,
                Course_ID=course.Course_ID,
                Status="enrolled"
            )
            created = enrollment_repo.create(enrollment)
            enrollments.append(created.to_dict())
    
    if errors:
        return jsonify({
            "status": "partial",
            "enrollments": enrollments,
            "errors": errors
        }), 200
    
    return jsonify({
        "status": "success",
        "enrollments": enrollments,
        "message": f"Successfully enrolled in {len(enrollments)} course(s)"
    }), 201

