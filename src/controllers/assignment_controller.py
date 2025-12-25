"""
Assignment Controller
Handles assignment management for instructors/TAs and submission for students
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from repositories.repository_factory import RepositoryFactory
from services.assignment_service import get_assignment_service
from core.user_helper import get_user_data
from core.role_auth import requires_role
from datetime import datetime
import os

assignment_bp = Blueprint('assignment', __name__, url_prefix='/assignments')

# Initialize service
assignment_service = get_assignment_service()
assignment_repo = RepositoryFactory.get_repository('assignment')
assignment_service.assignment_repo.create_table()
assignment_service.submission_repo.create_table()

# Initialize grading suggestion table if available
try:
    grading_repo = RepositoryFactory.get_repository('grading_suggestion')
    if grading_repo:
        grading_repo.create_table()
except Exception as e:
    print(f"Note: Grading suggestion repository not available: {e}")


@assignment_bp.route('/', methods=['GET'])
def assignments_page():
    """Assignment list page - shows different views based on role"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_id = session.get('user_id')
    user_data = get_user_data(user_id)
    
    # Check role
    from core.role_auth import get_user_role
    role = get_user_role(user_id)
    
    if role == 'Student':
        return redirect(url_for('assignment.student_assignments'))
    elif role in ['Instructor', 'TA']:
        return redirect(url_for('assignment.instructor_assignments'))
    else:
        return redirect(url_for('overview.overview_page'))


@assignment_bp.route('/student', methods=['GET'])
@requires_role('Student')
def student_assignments():
    """View assignments as a student"""
    try:
        user_id = session.get('user_id')
        user_data = get_user_data(user_id)
        
        # Get student ID
        student_repo = RepositoryFactory.get_repository('student')
        student = student_repo.get_by_user_id(user_id) if student_repo else None
        
        if not student:
            return redirect(url_for('overview.overview_page'))
        
        student_id = student.Student_ID
        
        # Get all courses the student is enrolled in
        enrollment_repo = RepositoryFactory.get_repository('enrollment')
        enrollments = enrollment_repo.get_by_student(student_id) if enrollment_repo else []
        course_ids = [e.Course_ID for e in enrollments]
        
        # Get all assignments for these courses
        all_assignments = []
        course_repo = RepositoryFactory.get_repository('course')
        
        for course_id in course_ids:
            assignments = assignment_service.get_assignments_by_course(course_id)
            course = course_repo.get_by_id(course_id) if course_repo else None
            
            for assignment in assignments:
                # Check if student has submitted
                submission = assignment_service.submission_repo.get_by_student_and_assignment(
                    student_id, assignment.Assignment_ID
                )
                
                assignment_dict = assignment.to_dict()
                assignment_dict['course_name'] = course.Course_Name if course else f'Course {course_id}'
                assignment_dict['has_submission'] = submission is not None
                assignment_dict['submission_status'] = submission.Status if submission else None
                assignment_dict['submission_grade'] = submission.Grade if submission else None
                assignment_dict['is_past_due'] = datetime.now() > assignment.Due_Date if assignment.Due_Date else False
                
                all_assignments.append(assignment_dict)
        
        # Sort by due date
        all_assignments.sort(key=lambda x: x['due_date'] if x['due_date'] else '9999-12-31')
        
        return render_template('student_assignments.html',
                             user_data=user_data,
                             assignments=all_assignments,
                             student_id=student_id)
    except Exception as e:
        print(f"Error loading student assignments: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500


@assignment_bp.route('/student/<int:assignment_id>', methods=['GET'])
@requires_role('Student')
def view_assignment(assignment_id):
    """View assignment details and submit"""
    try:
        user_id = session.get('user_id')
        user_data = get_user_data(user_id)
        
        # Get student ID
        student_repo = RepositoryFactory.get_repository('student')
        student = student_repo.get_by_user_id(user_id) if student_repo else None
        
        if not student:
            return redirect(url_for('overview.overview_page'))
        
        student_id = student.Student_ID
        
        # Get assignment
        assignment = assignment_service.get_assignment(assignment_id)
        if not assignment:
            return "Assignment not found", 404
        
        # Check if student is enrolled in the course
        enrollment_repo = RepositoryFactory.get_repository('enrollment')
        enrollments = enrollment_repo.get_by_student(student_id) if enrollment_repo else []
        enrollment = next((e for e in enrollments if e.Course_ID == assignment.Course_ID), None)
        
        if not enrollment:
            return "You are not enrolled in this course", 403
        
        # Get course info
        course_repo = RepositoryFactory.get_repository('course')
        course = course_repo.get_by_id(assignment.Course_ID) if course_repo else None
        
        # Get existing submission
        submission = assignment_service.submission_repo.get_by_student_and_assignment(
            student_id, assignment_id
        )
        
        assignment_dict = assignment.to_dict()
        assignment_dict['course_name'] = course.Course_Name if course else f'Course {assignment.Course_ID}'
        
        submission_dict = submission.to_dict() if submission else None
        
        return render_template('assignment_detail.html',
                             user_data=user_data,
                             assignment=assignment_dict,
                             submission=submission_dict,
                             student_id=student_id)
    except Exception as e:
        print(f"Error loading assignment: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500


@assignment_bp.route('/student/<int:assignment_id>/submit', methods=['POST'])
@requires_role('Student')
def submit_assignment(assignment_id):
    """Submit an assignment"""
    try:
        user_id = session.get('user_id')
        
        # Get student ID
        student_repo = RepositoryFactory.get_repository('student')
        student = student_repo.get_by_user_id(user_id) if student_repo else None
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        student_id = student.Student_ID
        
        # Get assignment
        assignment = assignment_service.get_assignment(assignment_id)
        if not assignment:
            return jsonify({'error': 'Assignment not found'}), 404
        
        # Handle file upload
        file_path = None
        file_name = None
        
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                # Save file (simplified - should use proper file handling)
                upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'uploads', 'assignments')
                os.makedirs(upload_folder, exist_ok=True)
                
                file_name = file.filename
                file_path = os.path.join(upload_folder, f"{assignment_id}_{student_id}_{file_name}")
                file.save(file_path)
                
                # Store relative path for database
                file_path = f"/static/uploads/assignments/{assignment_id}_{student_id}_{file_name}"
        
        # Get submission text if provided
        submission_text = request.form.get('submission_text', '').strip()
        
        # Validate that either file or text is provided
        if not submission_text and not file_path:
            return jsonify({'error': 'Please provide either a file or text submission'}), 400
        
        print(f"[SUBMIT] Submitting assignment {assignment_id} for student {student_id}")
        print(f"[SUBMIT] Has text: {bool(submission_text)}, Has file: {bool(file_path)}")
        print(f"[SUBMIT] Text length: {len(submission_text) if submission_text else 0}")
        
        # Submit assignment
        submission = assignment_service.submit_assignment(
            assignment_id, student_id, file_path, file_name, submission_text
        )
        
        print(f"[SUBMIT] Submission created: ID={submission.Submission_ID}, Status={submission.Status}")
        
        # Reload submission from database to get the latest grade if AI grading completed
        updated_submission = assignment_service.submission_repo.get_by_id(submission.Submission_ID)
        submission_dict = updated_submission.to_dict() if updated_submission else submission.to_dict()
        
        return jsonify({
            'success': True,
            'message': 'Assignment submitted successfully',
            'submission': submission_dict,
            'graded': updated_submission.Grade is not None if updated_submission else False
        })
    except Exception as e:
        print(f"Error submitting assignment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@assignment_bp.route('/create', methods=['GET'])
@requires_role('Instructor', 'TA')
def create_assignment_page():
    """Page to create a new assignment"""
    try:
        user_id = session.get('user_id')
        user_data = get_user_data(user_id)
        
        # Get instructor ID
        instructor_repo = RepositoryFactory.get_repository('instructor')
        instructor = instructor_repo.get_by_user_id(user_id) if instructor_repo else None
        
        if not instructor:
            return redirect(url_for('overview.overview_page'))
        
        instructor_id = instructor.Instructor_ID
        
        # Get courses taught by this instructor
        course_repo = RepositoryFactory.get_repository('course')
        courses = course_repo.get_by_instructor(instructor_id) if course_repo else []
        
        return render_template('create_assignment.html',
                             user_data=user_data,
                             courses=courses)
    except Exception as e:
        print(f"Error loading create assignment page: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500


@assignment_bp.route('/instructor', methods=['GET'])
@requires_role('Instructor', 'TA')
def instructor_assignments():
    """View and manage assignments as instructor/TA"""
    try:
        user_id = session.get('user_id')
        user_data = get_user_data(user_id)
        
        # Get instructor ID (for TA, we need to find the instructor they're assisting)
        instructor_repo = RepositoryFactory.get_repository('instructor')
        instructor = instructor_repo.get_by_user_id(user_id) if instructor_repo else None
        
        ta_repo = RepositoryFactory.get_repository('teaching_assistant')
        ta = ta_repo.get_by_user_id(user_id) if ta_repo else None
        
        # For assignments, Created_By should be Instructor_ID
        # If TA, we'll show assignments from courses they're assigned to
        if instructor:
            instructor_id = instructor.Instructor_ID
            assignments = assignment_service.get_assignments_by_creator(instructor_id)
        elif ta:
            # For TA, get assignments from their assigned course(s)
            assigned_course_id = ta.Assigned_Course_ID if ta else None
            if assigned_course_id:
                # Get all assignments for the TA's assigned course
                assignments = assignment_service.get_assignments_by_course(assigned_course_id)
            else:
                # If no course assigned, show empty list
                assignments = []
            instructor_id = None  # TA doesn't have Instructor_ID
        else:
            return redirect(url_for('overview.overview_page'))
        
        # Convert assignments to dictionaries for template
        course_repo = RepositoryFactory.get_repository('course')
        assignments_list = []
        for assignment in assignments:
            course = course_repo.get_by_id(assignment.Course_ID) if course_repo else None
            assignment_dict = assignment.to_dict()
            assignment_dict['course_name'] = course.Course_Name if course else f'Course {assignment.Course_ID}'
            assignments_list.append(assignment_dict)
        
        return render_template('instructor_assignments.html',
                             user_data=user_data,
                             assignments=assignments_list,
                             instructor_id=instructor_id)
    except Exception as e:
        print(f"Error loading instructor assignments: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500


# API endpoints for CRUD operations
@assignment_bp.route('/api', methods=['POST'])
@requires_role('Instructor', 'TA')
def create_assignment_api():
    """Create a new assignment (API)"""
    try:
        user_id = session.get('user_id')
        data = request.json
        
        # Get instructor ID (only instructors can create assignments, TAs assist)
        instructor_repo = RepositoryFactory.get_repository('instructor')
        instructor = instructor_repo.get_by_user_id(user_id) if instructor_repo else None
        
        if not instructor:
            return jsonify({'error': 'Only instructors can create assignments'}), 403
        
        instructor_id = instructor.Instructor_ID
        
        # Parse due date - handle datetime-local format (YYYY-MM-DDTHH:mm)
        due_date = None
        if data.get('due_date'):
            try:
                # Convert datetime-local format to datetime object
                due_date_str = data['due_date']
                if 'T' in due_date_str:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
                else:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            except Exception as e:
                print(f"Error parsing due date: {e}")
                return jsonify({'error': 'Invalid date format'}), 400
        
        if not due_date:
            return jsonify({'error': 'Due date is required'}), 400
        
        assignment = assignment_service.create_assignment(
            course_id=data['course_id'],
            title=data['title'],
            description=data.get('description'),
            instructions=data.get('instructions'),
            due_date=due_date,
            max_score=float(data.get('max_score', 100)),
            assignment_type=data.get('assignment_type'),
            created_by=instructor_id,
            allowed_file_types=data.get('allowed_file_types'),
            max_file_size_mb=int(data.get('max_file_size_mb', 10)),
            correct_answer=data.get('correct_answer'),
            is_auto_graded=bool(data.get('is_auto_graded', False))
        )
        
        return jsonify({
            'success': True,
            'assignment': assignment.to_dict()
        }), 201
    except Exception as e:
        print(f"Error creating assignment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@assignment_bp.route('/<int:assignment_id>/submissions', methods=['GET'])
@requires_role('Instructor', 'TA')
def view_submissions(assignment_id):
    """View all submissions for an assignment (page)"""
    try:
        user_id = session.get('user_id')
        user_data = get_user_data(user_id)
        
        # Get assignment
        assignment = assignment_service.get_assignment(assignment_id)
        if not assignment:
            return "Assignment not found", 404
        
        # Get course info
        course_repo = RepositoryFactory.get_repository('course')
        course = course_repo.get_by_id(assignment.Course_ID) if course_repo else None
        
        # Get submissions
        submissions = assignment_service.get_submissions_by_assignment(assignment_id)
        
        # Enrich with student info
        student_repo = RepositoryFactory.get_repository('student')
        user_repo = RepositoryFactory.get_repository('user')
        
        submissions_list = []
        for submission in submissions:
            student = student_repo.get_by_id(submission.Student_ID) if student_repo else None
            student_user = None
            if student and user_repo:
                student_user = user_repo.get_by_id(student.User_ID)
            
            submission_dict = submission.to_dict()
            submission_dict['student_name'] = student_user.Username if student_user else f'Student {submission.Student_ID}'
            submissions_list.append(submission_dict)
        
        assignment_dict = assignment.to_dict()
        assignment_dict['course_name'] = course.Course_Name if course else f'Course {assignment.Course_ID}'
        
        return render_template('view_submissions.html',
                             user_data=user_data,
                             assignment=assignment_dict,
                             submissions=submissions_list)
    except Exception as e:
        print(f"Error viewing submissions: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500


@assignment_bp.route('/<int:assignment_id>/edit', methods=['GET'])
@requires_role('Instructor', 'TA')
def edit_assignment_page(assignment_id):
    """Page to edit an assignment"""
    try:
        user_id = session.get('user_id')
        user_data = get_user_data(user_id)
        
        # Get assignment
        assignment = assignment_service.get_assignment(assignment_id)
        if not assignment:
            return "Assignment not found", 404
        
        # Check if user is the creator
        instructor_repo = RepositoryFactory.get_repository('instructor')
        instructor = instructor_repo.get_by_user_id(user_id) if instructor_repo else None
        
        if instructor and assignment.Created_By != instructor.Instructor_ID:
            return "You don't have permission to edit this assignment", 403
        
        # Get course info
        course_repo = RepositoryFactory.get_repository('course')
        course = course_repo.get_by_id(assignment.Course_ID) if course_repo else None
        
        assignment_dict = assignment.to_dict()
        assignment_dict['course_name'] = course.Course_Name if course else f'Course {assignment.Course_ID}'
        
        return render_template('edit_assignment.html',
                             user_data=user_data,
                             assignment=assignment_dict)
    except Exception as e:
        print(f"Error loading edit assignment page: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500


@assignment_bp.route('/api/<int:assignment_id>', methods=['PUT'])
@requires_role('Instructor', 'TA')
def update_assignment(assignment_id):
    """Update an assignment (API)"""
    try:
        user_id = session.get('user_id')
        data = request.json
        
        # Get assignment
        assignment = assignment_service.get_assignment(assignment_id)
        if not assignment:
            return jsonify({'error': 'Assignment not found'}), 404
        
        # Check if user is the creator
        instructor_repo = RepositoryFactory.get_repository('instructor')
        instructor = instructor_repo.get_by_user_id(user_id) if instructor_repo else None
        
        if instructor and assignment.Created_By != instructor.Instructor_ID:
            return jsonify({'error': 'You don\'t have permission to edit this assignment'}), 403
        
        # Parse due date
        due_date = None
        if data.get('due_date'):
            try:
                due_date_str = data['due_date']
                if 'T' in due_date_str:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
                else:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            except Exception as e:
                print(f"Error parsing due date: {e}")
                return jsonify({'error': 'Invalid date format'}), 400
        
        # Update assignment fields
        assignment.Title = data.get('title', assignment.Title)
        assignment.Description = data.get('description', assignment.Description)
        assignment.Instructions = data.get('instructions', assignment.Instructions)
        if due_date:
            assignment.Due_Date = due_date
        assignment.Max_Score = float(data.get('max_score', assignment.Max_Score))
        assignment.Assignment_Type = data.get('assignment_type', assignment.Assignment_Type)
        assignment.Allowed_File_Types = data.get('allowed_file_types', assignment.Allowed_File_Types)
        assignment.Max_File_Size_MB = int(data.get('max_file_size_mb', assignment.Max_File_Size_MB))
        assignment.Is_Auto_Graded = bool(data.get('is_auto_graded', assignment.Is_Auto_Graded))
        assignment.Correct_Answer = data.get('correct_answer', assignment.Correct_Answer)
        
        # Update in database
        assignment_service.update_assignment(assignment)
        
        return jsonify({
            'success': True,
            'assignment': assignment.to_dict()
        })
    except Exception as e:
        print(f"Error updating assignment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@assignment_bp.route('/api/<int:assignment_id>/submissions', methods=['GET'])
@requires_role('Instructor', 'TA')
def get_submissions(assignment_id):
    """Get all submissions for an assignment (API)"""
    try:
        submissions = assignment_service.get_submissions_by_assignment(assignment_id)
        
        # Enrich with student info
        student_repo = RepositoryFactory.get_repository('student')
        user_repo = RepositoryFactory.get_repository('user')
        
        result = []
        for submission in submissions:
            student = student_repo.get_by_id(submission.Student_ID) if student_repo else None
            student_user = None
            if student and user_repo:
                student_user = user_repo.get_by_id(student.User_ID)
            
            submission_dict = submission.to_dict()
            submission_dict['student_name'] = student_user.Username if student_user else f'Student {submission.Student_ID}'
            result.append(submission_dict)
        
        return jsonify(result)
    except Exception as e:
        print(f"Error getting submissions: {e}")
        return jsonify({'error': str(e)}), 500


@assignment_bp.route('/api/submissions/<int:submission_id>/auto-grade', methods=['POST'])
@requires_role('Instructor', 'TA')
def trigger_auto_grade(submission_id):
    """Manually trigger auto-grading for a submission (for testing/debugging)"""
    try:
        from services.ai_grading_service import get_ai_grading_service
        
        ai_grading_service = get_ai_grading_service()
        result = ai_grading_service.auto_grade_submission(submission_id)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        print(f"Error triggering auto-grade: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@assignment_bp.route('/api/submissions/<int:submission_id>/grade', methods=['PUT'])
@requires_role('Instructor', 'TA')
def grade_submission(submission_id):
    """Grade a submission"""
    try:
        user_id = session.get('user_id')
        data = request.json
        
        # Get instructor ID
        instructor_repo = RepositoryFactory.get_repository('instructor')
        instructor = instructor_repo.get_by_user_id(user_id) if instructor_repo else None
        
        ta_repo = RepositoryFactory.get_repository('teaching_assistant')
        ta = ta_repo.get_by_user_id(user_id) if ta_repo else None
        
        # For grading, we need Instructor_ID (TAs can grade but need to use instructor's ID or a special handling)
        # Since Graded_By references Instructor_ID, we'll use the instructor's ID
        # If TA, we'll need to get the instructor for the course
        grader_id = None
        if instructor:
            grader_id = instructor.Instructor_ID
        elif ta:
            # For TA, get the instructor for the assignment's course
            assignment = assignment_service.get_assignment_by_submission(submission_id)
            if assignment:
                course_repo = RepositoryFactory.get_repository('course')
                course = course_repo.get_by_id(assignment.Course_ID) if course_repo else None
                if course and course.Instructor_ID:
                    grader_id = course.Instructor_ID
                else:
                    # Fallback: use TA's assigned course instructor
                    course = course_repo.get_by_id(ta.Assigned_Course_ID) if course_repo and ta.Assigned_Course_ID else None
                    if course:
                        grader_id = course.Instructor_ID
        
        if not grader_id:
            return jsonify({'error': 'Unable to determine grader. Only instructors/TAs can grade assignments'}), 403
        
        grade = float(data.get('grade', 0))
        feedback = data.get('feedback', '')
        
        # Grade the submission (not AI-graded when manually graded by instructor)
        submission = assignment_service.grade_submission(
            submission_id, grade, feedback, grader_id, is_ai_graded=False
        )
        
        return jsonify({
            'success': True,
            'submission': submission.to_dict()
        })
    except Exception as e:
        print(f"Error grading submission: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@assignment_bp.route('/api/submissions/<int:submission_id>/request-review', methods=['POST'])
@requires_role('Student')
def request_review(submission_id):
    """Request a manual review of an AI-graded submission"""
    try:
        user_id = session.get('user_id')
        
        # Get student ID
        student_repo = RepositoryFactory.get_repository('student')
        student = student_repo.get_by_user_id(user_id) if student_repo else None
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        student_id = student.Student_ID
        
        # Get submission and verify it belongs to the student
        submission = assignment_service.submission_repo.get_by_id(submission_id)
        if not submission:
            return jsonify({'error': 'Submission not found'}), 404
        
        if submission.Student_ID != student_id:
            return jsonify({'error': 'Unauthorized: This submission does not belong to you'}), 403
        
        # Verify it's an AI-graded submission
        if not submission.Is_AI_Graded:
            return jsonify({'error': 'This submission was not AI-graded'}), 400
        
        # Get the review comment from request
        data = request.json or {}
        review_comment = data.get('comment', '') or data.get('review_comment', '') or 'Student requested manual review of AI grade.'
        
        # Update submission to request review
        submission.Review_Requested = True
        submission.Review_Comment = review_comment.strip()
        submission.Status = 'review_requested'
        
        updated = assignment_service.submission_repo.update(submission)
        
        if updated:
            return jsonify({
                'success': True,
                'message': 'Review request submitted successfully',
                'submission': updated.to_dict() if hasattr(updated, 'to_dict') else submission.to_dict()
            })
        else:
            return jsonify({'error': 'Failed to update submission'}), 500
            
    except Exception as e:
        print(f"Error requesting review: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
