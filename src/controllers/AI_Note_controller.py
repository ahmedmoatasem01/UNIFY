from flask import Blueprint, request, jsonify, render_template, session
from werkzeug.utils import secure_filename
import os
from docx import Document
import PyPDF2
from transformers import pipeline, AutoTokenizer

from repositories.repository_factory import RepositoryFactory

ai_note_bp = Blueprint('ai_note_bp', __name__)

# Use absolute path for uploads folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "notes")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED = {"txt", "pdf", "docx"}

# Model configuration - loaded lazily on first use
model_name = "sshleifer/distilbart-cnn-12-6"
summarizer = None
tokenizer = None

def _load_model():
    """Lazy load the model and tokenizer on first use."""
    global summarizer, tokenizer
    if summarizer is None or tokenizer is None:
        try:
            # Load the summarization pipeline with a specific model
            # Using "sshleifer/distilbart-cnn-12-6" as it was the default, but specifying it explicitly.
            # This model has a max input size of 1024 tokens.
            print("Loading summarization model... This may take a few minutes on first use.")
            summarizer = pipeline("summarization", model=model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            print("Model loaded successfully!")
        except Exception as e:
            error_msg = str(e)
            if "huggingface.co" in error_msg or "connection" in error_msg.lower():
                raise Exception(
                    "Cannot connect to Hugging Face to download the model. "
                    "Please ensure you have an internet connection and run the download script first:\n"
                    "python download_model.py\n"
                    "Or download manually from: https://huggingface.co/sshleifer/distilbart-cnn-12-6"
                )
            else:
                raise Exception(f"Failed to load model: {error_msg}")
    return summarizer, tokenizer

repo = RepositoryFactory.get_repository("ai_note")

def extract_text(path):
    ext = path.split(".")[-1].lower()

    if ext == "txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    if ext == "pdf":
        text = ""
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    if ext == "docx":
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])

    return ""


def summarize_text(text):
    """
    Summarize text by splitting it into chunks and combining summaries.
    Handles long texts that exceed the model's token limit.
    """
    # Load model on first use
    summarizer, tokenizer = _load_model()
    
    # Split the text into chunks that are smaller than the model's maximum input size
    max_chunk_tokens = 512  # A safe margin below the model's 1024 token limit
    text_chunks = []
    current_chunk = ""
    sentences = text.split('.')  # Split by sentences as a simple heuristic
    
    for sentence in sentences:
        # Add a period back to the sentence for better summarization
        sentence = sentence.strip() + "." if sentence.strip() else ""
        if not sentence:
            continue
        
        # Check if adding the current sentence exceeds the chunk limit
        if len(tokenizer.encode(current_chunk + " " + sentence)) > max_chunk_tokens:
            # If it does, add the current chunk to the list and start a new one
            text_chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            # Otherwise, add the sentence to the current chunk
            current_chunk += " " + sentence
    
    # Add the last chunk if it's not empty
    if current_chunk.strip():
        text_chunks.append(current_chunk.strip())
    
    summaries = []
    for i, chunk in enumerate(text_chunks):
        try:
            # Adjust max_length and min_length for each chunk based on its size
            # A simple approach: max_length is 80% of chunk tokens, min_length is 20%
            chunk_token_count = len(tokenizer.encode(chunk))
            chunk_max_length = int(chunk_token_count * 0.8)
            chunk_min_length = int(chunk_token_count * 0.2)
            
            # Ensure min_length is at least 1 and max_length is greater than min_length
            chunk_min_length = max(1, chunk_min_length)
            chunk_max_length = max(chunk_min_length + 1, chunk_max_length)
            
            summary = summarizer(chunk, max_length=chunk_max_length, min_length=chunk_min_length, do_sample=False)[0]['summary_text']
            summaries.append(summary)
        except Exception as e:
            # Catch any exceptions during summarization and print an error
            print(f"Could not summarize chunk {i+1}: {chunk[:100]}...")
            print(f"Error: {e}")
            continue
    
    # Join the summaries of individual chunks
    summary_text = " ".join(summaries)
    return summary_text


@ai_note_bp.route("/ai-note-summarizer", methods=["GET"])
def page():
    """Redirect to notes page where summarizer is integrated"""
    from flask import redirect, url_for
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

    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED:
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    # Extract text
    text = extract_text(path)
    if len(text.strip()) < 20:
        return jsonify({"error": "File text too short"}), 400

    # Summarize using chunking for long texts
    try:
        summary = summarize_text(text)
    except Exception as e:
        error_msg = str(e)
        print(f"Summarization error: {error_msg}")
        
        # Provide user-friendly error message
        if "huggingface.co" in error_msg or "connection" in error_msg.lower() or "couldn't connect" in error_msg.lower():
            user_error = (
                "Cannot download the AI model. Please ensure you have an internet connection "
                "and run: python download_model.py\n\n"
                "See MODEL_DOWNLOAD_INSTRUCTIONS.md for detailed instructions."
            )
        else:
            user_error = f"Failed to summarize: {error_msg}"
        
        return jsonify({"error": user_error}), 500

    # Save summary into DB
    try:
        saved_note = repo.save_summary(student_id, filename, summary)
    except Exception as e:
        print(f"Database save error: {e}")
        return jsonify({"error": "Failed to save summary"}), 500

    return jsonify({
        "summary": summary,
        "original_text": text,
        "note_id": saved_note.Note_ID
    })


@ai_note_bp.route("/api/notes", methods=["GET"])
def api_get_notes():
    """Get all notes for the current student"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session.get('user_id')
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    student_id = student.Student_ID
    
    try:
        notes = repo.get_by_student_id(student_id)
        return jsonify([{
            "note_id": note.Note_ID,
            "original_file": note.Original_File,
            "summary_text": note.Summary_Text,
            "upload_date": note.Upload_Date.isoformat() if hasattr(note.Upload_Date, 'isoformat') else str(note.Upload_Date)
        } for note in notes])
    except Exception as e:
        print(f"Error fetching notes: {e}")
        return jsonify({"error": "Failed to fetch notes"}), 500


@ai_note_bp.route("/api/notes/<int:note_id>", methods=["DELETE"])
def api_delete_note(note_id):
    """Delete a note by ID"""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session.get('user_id')
    student_repo = RepositoryFactory.get_repository("student")
    student = student_repo.get_by_user_id(user_id)
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    student_id = student.Student_ID
    
    try:
        # Verify note belongs to student
        note = repo.get_by_id(note_id)
        if not note:
            return jsonify({"error": "Note not found"}), 404
        
        if note.Student_ID != student_id:
            return jsonify({"error": "Unauthorized"}), 403
        
        repo.delete(note_id)
        return jsonify({"message": "Note deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting note: {e}")
        return jsonify({"error": "Failed to delete note"}), 500
