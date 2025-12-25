"""
Course Registration Controller
Handles course registration page and optimization API
"""
from datetime import time
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from repositories.repository_factory import RepositoryFactory
from services.course_optimization_service import get_course_optimization_service
from core.user_helper import get_user_data

course_reg_bp = Blueprint("course_registration", __name__, url_prefix="/course-registration")
optimization_service = get_course_optimization_service()


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
    
    # Get schedule slot repository using factory pattern
    slot_repo = RepositoryFactory.get_repository('course_schedule_slot')
    
    # Get all unique courses from schedule slots
    from core.db_singleton import DatabaseConnection
    db_connection = DatabaseConnection.get_instance()
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
    
    # Get unique course codes with their sections from the optimized schedule
    # Group by course_code and track which sections were selected
    course_sections_map = {}
    for slot in schedule:
        course_code = slot.get("course_code")
        section = slot.get("section")
        if course_code:
            if course_code not in course_sections_map:
                course_sections_map[course_code] = set()
            course_sections_map[course_code].add(section)
    
    # Get repositories
    enrollment_repo = RepositoryFactory.get_repository("enrollment")
    schedule_repo = RepositoryFactory.get_repository("schedule")
    
    enrollments = []
    errors = []
    
    # Get database connection
    from core.db_singleton import DatabaseConnection
    import json
    db_connection = DatabaseConnection()
    conn = db_connection.get_connection()
    
    try:
        cursor = conn.cursor()
        
        for course_code, sections in course_sections_map.items():
            # Get Course_ID from Course_Schedule_Slot table
            cursor.execute("""
                SELECT DISTINCT Course_ID 
                FROM Course_Schedule_Slot 
                WHERE Course_Code = ?
            """, (course_code,))
            row = cursor.fetchone()
            
            if not row:
                errors.append(f"Course {course_code} not found in schedule")
                continue
            
            course_id = row[0]
            
            # Check if already enrolled
            existing = enrollment_repo.get_by_student(student_id)
            already_enrolled = any(e.Course_ID == course_id and e.Status == "enrolled" for e in existing)
            
            if already_enrolled:
                errors.append(f"Course {course_code} is already enrolled")
                continue
            
            # Create enrollment
            from models.enrollment import Enrollment
            enrollment = Enrollment(
                Student_ID=student_id,
                Course_ID=course_id,
                Status="enrolled"
            )
            created = enrollment_repo.create(enrollment)
            enrollments.append(created.to_dict())
        
        # Save the optimized schedule with specific sections to Schedule table
        # This allows us to filter which sections to show later
        import json
        schedule_json = json.dumps(schedule)
        
        # Check if student already has a schedule
        existing_schedule = schedule_repo.get_by_student(student_id)
        if existing_schedule:
            # Update existing schedule
            existing_schedule.Course_List = schedule_json
            existing_schedule.Optimized = True
            schedule_repo.update(existing_schedule)
        else:
            # Create new schedule
            from models.schedule import Schedule
            new_schedule = Schedule(
                Student_ID=student_id,
                Course_List=schedule_json,
                Optimized=True
            )
            schedule_repo.create(new_schedule)
            
    finally:
        conn.close()
    
    if errors:
        return jsonify({
            "status": "partial",
            "enrollments": enrollments,
            "errors": errors,
            "message": f"Enrolled in {len(enrollments)} course(s). Errors: {', '.join(errors)}"
        }), 200
    
    return jsonify({
        "status": "success",
        "enrollments": enrollments,
        "message": f"Successfully enrolled in {len(enrollments)} course(s) with optimized sections"
    }), 201


@course_reg_bp.route("/api/drop", methods=["POST"])
def api_drop_course():
    """
    Drop a course (delete enrollment from database).
    
    Request JSON:
    {
        "course_code": "CSAI 201" or "course_id": 123
    }
    """
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json(silent=True) or {}
    course_code = data.get("course_code")
    course_id = data.get("course_id")
    
    # Get student_id from session
    user_id = session.get('user_id')
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    if not student:
        return jsonify({"error": "Student record not found"}), 404
    
    student_id = student.Student_ID
    
    # Get repositories
    enrollment_repo = RepositoryFactory.get_repository("enrollment")
    from core.db_singleton import DatabaseConnection
    db_connection = DatabaseConnection()
    conn = db_connection.get_connection()
    
    try:
        cursor = conn.cursor()
        
        # If course_code provided, find course_id
        if course_code and not course_id:
            cursor.execute("""
                SELECT DISTINCT Course_ID 
                FROM Course_Schedule_Slot 
                WHERE Course_Code = ?
            """, (course_code,))
            row = cursor.fetchone()
            if not row:
                return jsonify({"error": f"Course {course_code} not found"}), 404
            course_id = row[0]
        
        if not course_id:
            return jsonify({"error": "Course code or ID required"}), 400
        
        # Find enrollment
        existing = enrollment_repo.get_by_student(student_id)
        enrollment = next((e for e in existing if e.Course_ID == course_id), None)
        
        if not enrollment:
            return jsonify({"error": "Course not enrolled"}), 404
        
        # Delete enrollment
        enrollment_repo.delete(enrollment.Enrollment_ID)
        
        return jsonify({
            "status": "success",
            "message": f"Successfully dropped course"
        }), 200
        
    finally:
        conn.close()


@course_reg_bp.route("/api/my-schedule", methods=["GET"])
def api_my_schedule():
    """
    Get enrolled courses with schedule slots for the current student.
    Returns schedule in the same format as /api/optimize for calendar display.
    """
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get student_id from session
    user_id = session.get('user_id')
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    if not student:
        return jsonify({"error": "Student record not found"}), 404
    
    student_id = student.Student_ID
    
    # Get enrollments
    enrollment_repo = RepositoryFactory.get_repository("enrollment")
    enrollments = enrollment_repo.get_by_student(student_id)
    
    if not enrollments:
        return jsonify({"status": "ok", "schedule": []})
    
    # Get course IDs
    course_ids = [e.Course_ID for e in enrollments if e.Status == "enrolled"]
    
    if not course_ids:
        return jsonify({"status": "ok", "schedule": []})
    
    # Get the saved optimized schedule to filter by specific sections
    schedule_repo = RepositoryFactory.get_repository("schedule")
    saved_schedule = schedule_repo.get_by_student(student_id)
    
    # Build a set of (course_code, section) tuples from the saved optimized schedule
    enrolled_sections = set()
    if saved_schedule and saved_schedule.Course_List:
        import json
        try:
            optimized_slots = json.loads(saved_schedule.Course_List)
            for slot in optimized_slots:
                course_code = slot.get("course_code")
                section = slot.get("section")
                if course_code and section is not None:
                    enrolled_sections.add((course_code, section))
        except (json.JSONDecodeError, TypeError):
            pass  # If JSON parsing fails, fall back to showing all sections
    
    # Get schedule slots for enrolled courses
    from core.db_singleton import DatabaseConnection
    db_connection = DatabaseConnection()
    conn = db_connection.get_connection()
    
    schedule = []
    try:
        cursor = conn.cursor()
        # Build query with placeholders
        placeholders = ','.join(['?' for _ in course_ids])
        query = f"""
            SELECT Course_Code, Section, Day, Start_Time, End_Time, Slot_Type, Sub_Type
            FROM Course_Schedule_Slot
            WHERE Course_ID IN ({placeholders})
            AND Academic_Year = ?
            AND Term = ?
            ORDER BY Day, Start_Time
        """
        academic_year = request.args.get("academic_year", 2025, type=int)
        term = request.args.get("term", "SPRING", type=str)
        params = list(course_ids) + [academic_year, term]
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        for row in rows:
            course_code = row[0]
            section = row[1]
            day = row[2]
            start_time = row[3]
            end_time = row[4]
            slot_type = row[5]
            sub_type = row[6]
            
            # Filter: Only include slots that match the enrolled sections
            # If we have saved optimized schedule, use it to filter
            # Otherwise, show all sections (for backward compatibility)
            if enrolled_sections and (course_code, section) not in enrolled_sections:
                continue
            
            # Convert time objects to HH:MM strings
            if isinstance(start_time, time):
                start_str = start_time.strftime("%H:%M")
            else:
                start_str = str(start_time)[:5] if len(str(start_time)) >= 5 else "08:00"
            
            if isinstance(end_time, time):
                end_str = end_time.strftime("%H:%M")
            else:
                end_str = str(end_time)[:5] if len(str(end_time)) >= 5 else "09:00"
            
            # Determine type (lecture or lab)
            slot_type_lower = (slot_type or "").lower()
            sub_type_upper = (sub_type or "").upper()
            if slot_type_lower == "lecture" or sub_type_upper == "LCTR":
                type_str = "lecture"
            else:
                type_str = "lab"
            
            schedule.append({
                "course_code": course_code,
                "course_name": course_code,  # Using code as name
                "type": type_str,
                "sub_type": sub_type or "LCTR",
                "section": section,
                "day": day,
                "start": start_str,
                "end": end_str
            })
    finally:
        conn.close()
    
    return jsonify({"status": "ok", "schedule": schedule})

