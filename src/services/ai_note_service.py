"""
AI Note Service
Handles AI summarization logic, text extraction, and file processing
"""
import os
from docx import Document
import PyPDF2
from transformers import pipeline, AutoTokenizer


class AINoteService:
    """Service for AI-powered note summarization"""
    
    def __init__(self):
        self.model_name = "sshleifer/distilbart-cnn-12-6"
        self.summarizer = None
        self.tokenizer = None
        self.upload_folder = None
        self.allowed_extensions = {"txt", "pdf", "docx"}
    
    def set_upload_folder(self, folder_path):
        """Set the upload folder path"""
        self.upload_folder = folder_path
        os.makedirs(folder_path, exist_ok=True)
    
    def _load_model(self):
        """Lazy load the model and tokenizer on first use"""
        if self.summarizer is None or self.tokenizer is None:
            try:
                print("Loading summarization model... This may take a few minutes on first use.")
                self.summarizer = pipeline("summarization", model=self.model_name)
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
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
        return self.summarizer, self.tokenizer
    
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def extract_text(self, file_path):
        """
        Extract text from various file formats (TXT, PDF, DOCX)
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text as string
        """
        ext = file_path.split(".")[-1].lower()
        
        if ext == "txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        
        if ext == "pdf":
            text = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        
        if ext == "docx":
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        
        return ""
    
    def summarize_text(self, text):
        """
        Summarize text by splitting it into chunks and combining summaries.
        Handles long texts that exceed the model's token limit.
        
        Args:
            text: Text to summarize
            
        Returns:
            Summarized text
        """
        # Load model on first use
        summarizer, tokenizer = self._load_model()
        
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
                
                summary = summarizer(
                    chunk, 
                    max_length=chunk_max_length, 
                    min_length=chunk_min_length, 
                    do_sample=False
                )[0]['summary_text']
                summaries.append(summary)
            except Exception as e:
                # Catch any exceptions during summarization and print an error
                print(f"Could not summarize chunk {i+1}: {chunk[:100]}...")
                print(f"Error: {e}")
                continue
        
        # Join the summaries of individual chunks
        summary_text = " ".join(summaries)
        return summary_text
    
    def process_file(self, file_path):
        """
        Process a file: extract text and generate summary
        
        Args:
            file_path: Path to the uploaded file
            
        Returns:
            Dictionary with original_text and summary
        """
        # Extract text from file
        original_text = self.extract_text(file_path)
        
        if not original_text.strip():
            raise ValueError("No text could be extracted from the file")
        
        # Generate summary
        summary = self.summarize_text(original_text)
        
        return {
            'original_text': original_text,
            'summary': summary,
            'word_count_original': len(original_text.split()),
            'word_count_summary': len(summary.split())
        }


# Singleton instance
_ai_note_service = None

def get_ai_note_service():
    """Get the singleton AI Note Service instance"""
    global _ai_note_service
    if _ai_note_service is None:
        _ai_note_service = AINoteService()
    return _ai_note_service

