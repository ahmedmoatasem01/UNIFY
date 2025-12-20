"""
Course Material Controller
Handles course material upload, download, and management
"""
from flask import Blueprint, request, jsonify, session, redirect, url_for, send_file, render_template
from repositories.repository_factory import RepositoryFactory
from models.course_material import CourseMaterial
from core.user_helper import get_user_data
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime

course_material_bp = Blueprint("course_material", __name__, url_prefix="/course-materials")


@course_material_bp.route("/")
def course_materials_main():
    """Main Course Materials page showing all courses"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_id = session.get('user_id')
    user_data = get_user_data(user_id)
    
    enrolled_courses = []
    instructor_courses = []
    
    # Get student courses
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    if student:
        try:
            enrollment_repo = RepositoryFactory.get_repository("enrollment")
            course_repo = RepositoryFactory.get_repository("course")
            enrollments = enrollment_repo.get_by_student(student.Student_ID)
            
            for enrollment in enrollments:
                if enrollment.Status == 'enrolled':
                    course = course_repo.get_by_id(enrollment.Course_ID)
                    if course:
                        enrolled_courses.append(course)
        except Exception as e:
            print(f"Error fetching enrolled courses: {e}")
    
    # Get instructor courses
    if user_data and user_data.get('role') == 'Instructor':
        try:
            instructor_repo = RepositoryFactory.get_repository("instructor")
            course_repo = RepositoryFactory.get_repository("course")
            instructor = instructor_repo.get_by_user_id(user_id)
            if instructor:
                instructor_courses = course_repo.get_by_instructor(instructor.Instructor_ID)
        except Exception as e:
            print(f"Error fetching instructor courses: {e}")
    
    return render_template('course_materials/index.html',
                         user_data=user_data,
                         enrolled_courses=enrolled_courses,
                         instructor_courses=instructor_courses)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf', 'pptx', 'ppt', 'doc', 'docx', 'xls', 'xlsx',
    'txt', 'jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov',
    'zip', 'rar'
}

# Material type mapping based on file extension
EXTENSION_TO_TYPE = {
    'pdf': 'pdf',
    'pptx': 'pptx', 'ppt': 'pptx',
    'doc': 'assignment', 'docx': 'assignment',
    'xls': 'assignment', 'xlsx': 'assignment',
    'mp4': 'video', 'avi': 'video', 'mov': 'video',
    'jpg': 'other', 'jpeg': 'other', 'png': 'other', 'gif': 'other',
    'txt': 'other', 'zip': 'other', 'rar': 'other'
}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_type_from_extension(filename):
    """Determine material type from file extension"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return EXTENSION_TO_TYPE.get(ext, 'other')


@course_material_bp.route("/course/<int:course_id>")
def course_materials_page(course_id):
    """Display course materials page for students"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_data = get_user_data(session.get('user_id'))
    course_repo = RepositoryFactory.get_repository("course")
    course = course_repo.get_by_id(course_id)
    
    if not course:
        return "Course not found", 404
    
    material_repo = RepositoryFactory.get_repository("course_material")
    materials = material_repo.get_by_course(course_id)
    
    # Group materials by week and topic
    materials_by_week = {}
    for material in materials:
        week = material.Week_Number or 0
        if week not in materials_by_week:
            materials_by_week[week] = {}
        topic = material.Topic or "General"
        if topic not in materials_by_week[week]:
            materials_by_week[week][topic] = []
        materials_by_week[week][topic].append(material)
    
    return render_template('course_materials/view.html', 
                         course=course, 
                         materials_by_week=materials_by_week,
                         user_data=user_data)


@course_material_bp.route("/course/<int:course_id>/upload", methods=["GET"])
def upload_materials_page(course_id):
    """Display upload page for instructors"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_data = get_user_data(session.get('user_id'))
    course_repo = RepositoryFactory.get_repository("course")
    course = course_repo.get_by_id(course_id)
    
    if not course:
        return "Course not found", 404
    
    # Check if user is instructor for this course
    instructor_repo = RepositoryFactory.get_repository("instructor")
    instructor = instructor_repo.get_by_user_id(session.get('user_id'))
    
    if not instructor or instructor.Instructor_ID != course.Instructor_ID:
        return "Unauthorized: Only the course instructor can upload materials", 403
    
    return render_template('course_materials/upload.html', 
                         course=course,
                         user_data=user_data)


@course_material_bp.route("/api/course/<int:course_id>", methods=["GET"])
def api_get_materials(course_id):
    """API endpoint to get all materials for a course"""
    material_repo = RepositoryFactory.get_repository("course_material")
    materials = material_repo.get_by_course(course_id)
    return jsonify([material.to_dict() for material in materials])


@course_material_bp.route("/api/course/<int:course_id>/week/<int:week_number>", methods=["GET"])
def api_get_materials_by_week(course_id, week_number):
    """API endpoint to get materials for a specific week"""
    material_repo = RepositoryFactory.get_repository("course_material")
    materials = material_repo.get_by_course_and_week(course_id, week_number)
    return jsonify([material.to_dict() for material in materials])


@course_material_bp.route("/api", methods=["POST"])
def api_upload_material():
    """API endpoint to upload a new course material"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Check if user is an instructor
    instructor_repo = RepositoryFactory.get_repository("instructor")
    instructor = instructor_repo.get_by_user_id(session.get('user_id'))
    
    if not instructor:
        return jsonify({"error": "Only instructors can upload materials"}), 403
    
    # Check if link or file upload
    link_url = request.form.get('link_url')
    
    if link_url:
        # Handle link submission
        course_id = int(request.form.get('course_id'))
        material_title = request.form.get('material_title', '').strip()
        description = request.form.get('description', '').strip()
        week_number = request.form.get('week_number')
        topic = request.form.get('topic', '').strip()
        
        if not material_title:
            return jsonify({"error": "Material title is required"}), 400
        
        course_repo = RepositoryFactory.get_repository("course")
        course = course_repo.get_by_id(course_id)
        
        if not course or course.Instructor_ID != instructor.Instructor_ID:
            return jsonify({"error": "Unauthorized"}), 403
        
        material = CourseMaterial(
            Course_ID=course_id,
            Instructor_ID=instructor.Instructor_ID,
            Material_Title=material_title,
            Material_Type='link',
            Link_URL=link_url,
            Description=description,
            Week_Number=int(week_number) if week_number else None,
            Topic=topic if topic else None
        )
    else:
        # Handle file upload
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        
        course_id = int(request.form.get('course_id'))
        material_title = request.form.get('material_title', '').strip() or file.filename
        description = request.form.get('description', '').strip()
        week_number = request.form.get('week_number')
        topic = request.form.get('topic', '').strip()
        
        course_repo = RepositoryFactory.get_repository("course")
        course = course_repo.get_by_id(course_id)
        
        if not course or course.Instructor_ID != instructor.Instructor_ID:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Save file
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  'uploads', 'course_materials')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Relative path for database
        relative_path = f"course_materials/{unique_filename}"
        
        material = CourseMaterial(
            Course_ID=course_id,
            Instructor_ID=instructor.Instructor_ID,
            Material_Title=material_title,
            Material_Type=get_file_type_from_extension(file.filename),
            File_Path=relative_path,
            Description=description,
            Week_Number=int(week_number) if week_number else None,
            Topic=topic if topic else None,
            File_Size=file_size
        )
    
    material_repo = RepositoryFactory.get_repository("course_material")
    created_material = material_repo.create(material)
    
    return jsonify(created_material.to_dict()), 201


@course_material_bp.route("/download/<int:material_id>", methods=["GET"])
def download_material(material_id):
    """Download a course material file"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    material_repo = RepositoryFactory.get_repository("course_material")
    material = material_repo.get_by_id(material_id)
    
    if not material:
        return "Material not found", 404
    
    if not material.File_Path:
        return "File not available", 404
    
    # Check if user is enrolled in the course or is the instructor
    enrollment_repo = RepositoryFactory.get_repository("enrollment")
    course_repo = RepositoryFactory.get_repository("course")
    course = course_repo.get_by_id(material.Course_ID)
    
    user_id = session.get('user_id')
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    has_access = False
    if course and course.Instructor_ID == material.Instructor_ID:
        instructor_repo = RepositoryFactory.get_repository("instructor")
        instructor = instructor_repo.get_by_user_id(user_id)
        has_access = instructor and instructor.Instructor_ID == material.Instructor_ID
    
    if not has_access and student:
        enrollments = enrollment_repo.get_by_student_id(student.Student_ID)
        has_access = any(e.Course_ID == material.Course_ID for e in enrollments)
    
    if not has_access:
        return "Unauthorized: You must be enrolled in this course", 403
    
    # Increment download count
    material_repo.increment_download_count(material_id)
    
    # Send file
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
    file_path = os.path.join(uploads_dir, material.File_Path)
    
    if not os.path.exists(file_path):
        return "File not found", 404
    
    return send_file(file_path, as_attachment=True, download_name=material.Material_Title)


@course_material_bp.route("/preview/<int:material_id>", methods=["GET"])
def preview_material(material_id):
    """Preview a course material (for PDFs and images)"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    material_repo = RepositoryFactory.get_repository("course_material")
    material = material_repo.get_by_id(material_id)
    
    if not material:
        return "Material not found", 404
    
    if not material.is_previewable():
        return redirect(url_for('course_material.download_material', material_id=material_id))
    
    if not material.File_Path:
        return "File not available", 404
    
    # Check access (same as download)
    enrollment_repo = RepositoryFactory.get_repository("enrollment")
    course_repo = RepositoryFactory.get_repository("course")
    course = course_repo.get_by_id(material.Course_ID)
    
    user_id = session.get('user_id')
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    has_access = False
    if course and course.Instructor_ID == material.Instructor_ID:
        instructor_repo = RepositoryFactory.get_repository("instructor")
        instructor = instructor_repo.get_by_user_id(user_id)
        has_access = instructor and instructor.Instructor_ID == material.Instructor_ID
    
    if not has_access and student:
        enrollments = enrollment_repo.get_by_student_id(student.Student_ID)
        has_access = any(e.Course_ID == material.Course_ID for e in enrollments)
    
    if not has_access:
        return "Unauthorized", 403
    
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
    file_path = os.path.join(uploads_dir, material.File_Path)
    
    if not os.path.exists(file_path):
        return "File not found", 404
    
    return send_file(file_path)


@course_material_bp.route("/api/<int:material_id>", methods=["DELETE"])
def api_delete_material(material_id):
    """API endpoint to delete a course material"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    material_repo = RepositoryFactory.get_repository("course_material")
    material = material_repo.get_by_id(material_id)
    
    if not material:
        return jsonify({"error": "Material not found"}), 404
    
    # Check if user is the instructor
    instructor_repo = RepositoryFactory.get_repository("instructor")
    instructor = instructor_repo.get_by_user_id(session.get('user_id'))
    
    if not instructor or instructor.Instructor_ID != material.Instructor_ID:
        return jsonify({"error": "Unauthorized: Only the instructor can delete materials"}), 403
    
    material_repo.delete(material_id)
    return jsonify({"message": "Material deleted successfully"}), 200

