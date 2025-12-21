"""
AI Note Controller (Refactored)
Handles HTTP requests/responses for AI note summarization
Business logic moved to services layer
"""
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from werkzeug.utils import secure_filename
import os

from repositories.repository_factory import RepositoryFactory
from services.ai_note_service import get_ai_note_service

ai_note_bp = Blueprint('ai_note_bp', __name__)

# Initialize service
ai_service = get_ai_note_service()

# Use absolute path for uploads folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "notes")
ai_service.set_upload_folder(UPLOAD_FOLDER)

# Repository
ai_note_repo = RepositoryFactory.get_repository("ai_note")


@ai_note_bp.route("/ai-note-summarizer", methods=["GET"])
def page():
    """Redirect to notes page where summarizer is integrated"""
    return redirect(url_for('notes_page'))


@ai_note_bp.route("/api/summarize", methods=["POST"])
def summarize_api():
    """Summarize uploaded file and save to database"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get student_id from user_id
    user_id = session.get('user_id')
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    student_id = student.Student_ID
    
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not ai_service.allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Please upload TXT, PDF, or DOCX files."}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Process file using service
        result = ai_service.process_file(filepath)
        
        # Save to database
        from models.ai_note import AiNote
        ai_note = AiNote(
            Student_ID=student_id,
            Title=filename,
            Original_Content=result['original_text'],
            Summary=result['summary']
        )
        created_note = ai_note_repo.create(ai_note)
        
        # Clean up uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            "success": True,
            "note_id": created_note.AI_Note_ID,
            "title": filename,
            "original_text": result['original_text'],
            "summary": result['summary'],
            "word_count_original": result['word_count_original'],
            "word_count_summary": result['word_count_summary']
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error during summarization: {e}")
        return jsonify({"error": f"Summarization failed: {str(e)}"}), 500


@ai_note_bp.route("/api/notes", methods=["GET"])
def get_notes():
    """Get all AI notes for current user"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session.get('user_id')
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    if not student:
        return jsonify([]), 200
    
    try:
        notes = ai_note_repo.get_by_student(student.Student_ID)
        return jsonify([note.to_dict() for note in notes]), 200
    except Exception as e:
        print(f"Error fetching notes: {e}")
        return jsonify({"error": "Failed to fetch notes"}), 500


@ai_note_bp.route("/api/notes/<int:note_id>", methods=["GET"])
def get_note(note_id):
    """Get a specific AI note"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        note = ai_note_repo.get_by_id(note_id)
        if not note:
            return jsonify({"error": "Note not found"}), 404
        return jsonify(note.to_dict()), 200
    except Exception as e:
        print(f"Error fetching note: {e}")
        return jsonify({"error": "Failed to fetch note"}), 500


@ai_note_bp.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    """Delete an AI note"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        success = ai_note_repo.delete(note_id)
        if success:
            return jsonify({"success": True, "message": "Note deleted"}), 200
        else:
            return jsonify({"error": "Note not found"}), 404
    except Exception as e:
        print(f"Error deleting note: {e}")
        return jsonify({"error": "Failed to delete note"}), 500

