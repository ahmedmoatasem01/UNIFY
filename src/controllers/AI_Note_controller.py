from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from docx import Document
import PyPDF2
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

from repositories.repository_factory import RepositoryFactory

ai_note_bp = Blueprint('ai_note_bp', __name__)

UPLOAD_FOLDER = "uploads/notes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED = {"txt", "pdf", "docx"}

# Load local model ONCE
MODEL_PATH = r"E:\bart-large-cnn"


tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH, local_files_only=True)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

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


@ai_note_bp.route("/ai-note-summarizer", methods=["GET"])
def page():
    return render_template("AI_Note_Summarizer.html")


@ai_note_bp.route("/api/summarize", methods=["POST"])
def summarize_api():

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

    # Summarize
    summary = summarizer(text, max_length=200, min_length=60, do_sample=False)[0]["summary_text"]

    # TODO: replace with actual logged-in student ID
    student_id = 1

    # Save summary into DB
    saved_note = repo.save_summary(student_id, filename, summary)

    return jsonify({
        "summary": summary,
        "original_text": text,
        "note_id": saved_note.Note_ID
    })
