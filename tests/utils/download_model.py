"""
Script to pre-download the Hugging Face model for AI Note Summarizer.
Run this script once to download and cache the model locally.

Usage:
    python download_model.py
"""
from transformers import pipeline, AutoTokenizer
import sys

MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

def download_model():
    """Download and cache the summarization model"""
    print("=" * 60)
    print("AI Note Summarizer - Model Downloader")
    print("=" * 60)
    print(f"\nDownloading model: {MODEL_NAME}")
    print("This may take several minutes depending on your internet speed...")
    print("The model will be cached locally for future use.\n")
    
    try:
        print("Step 1: Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        print("✓ Tokenizer downloaded successfully!")
        
        print("\nStep 2: Downloading model and creating pipeline...")
        summarizer = pipeline("summarization", model=MODEL_NAME)
        print("✓ Model downloaded successfully!")
        
        print("\n" + "=" * 60)
        print("SUCCESS! Model has been downloaded and cached.")
        print("You can now use the AI Note Summarizer feature.")
        print("=" * 60)
        
        # Test the model
        print("\nTesting the model with a sample text...")
        test_text = """
        Artificial intelligence (AI) is intelligence demonstrated by machines. 
        AI research is defined as the study of systems that perceive their environment 
        and take actions that maximize their chance of achieving their goals.
        """
        result = summarizer(test_text, max_length=50, min_length=20, do_sample=False)
        print(f"✓ Test summary: {result[0]['summary_text']}")
        print("\nModel is ready to use!")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR: Failed to download model")
        print("=" * 60)
        print(f"\nError details: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Ensure you have enough disk space (model is ~500MB)")
        print("3. Try running: pip install --upgrade transformers")
        print("4. Check if there are firewall/proxy issues blocking huggingface.co")
        return False

if __name__ == "__main__":
    success = download_model()
    sys.exit(0 if success else 1)

