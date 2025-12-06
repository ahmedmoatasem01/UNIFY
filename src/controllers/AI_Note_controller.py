from flask import Blueprint, render_template, request

ai_note_bp = Blueprint('ai_note_bp', __name__)

@ai_note_bp.route('/ai-note-summarizer', methods=['GET', 'POST'])
def ai_note_summarizer():
    summary = None
    if request.method == 'POST':
        file = request.files.get('noteFile')
        if file:
            text = file.read().decode('utf-8', errors='ignore')
            # Simple summary: first 200 chars (replace with AI later)
            summary = text[:200] + ('...' if len(text) > 200 else '')
    return render_template('AINoteSummarizer.html', summary=summary)