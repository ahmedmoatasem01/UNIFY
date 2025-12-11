"""
Alternative download script with SSL/TLS fixes and retry logic.
"""
from transformers import pipeline, AutoTokenizer
import sys
import ssl
import os

MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

def download_model_with_retry():
    """Download model with SSL fixes and retry logic"""
    print("=" * 60)
    print("AI Note Summarizer - Model Downloader (With SSL Fix)")
    print("=" * 60)
    
    # Try to fix SSL context issues
    try:
        # Create unverified SSL context (for testing only - not recommended for production)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        print("\n⚠ Using relaxed SSL verification (for troubleshooting)")
    except:
        pass
    
    print(f"\nDownloading model: {MODEL_NAME}")
    print("This may take several minutes...\n")
    
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}/{max_retries}...")
            
            # Method 1: Try with local_files_only=False explicitly
            print("  → Downloading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(
                MODEL_NAME,
                local_files_only=False,
                trust_remote_code=False
            )
            print("  ✓ Tokenizer downloaded!")
            
            print("  → Downloading model...")
            summarizer = pipeline(
                "summarization",
                model=MODEL_NAME,
                tokenizer=tokenizer,
                trust_remote_code=False
            )
            print("  ✓ Model downloaded!")
            
            print("\n" + "=" * 60)
            print("SUCCESS! Model downloaded and cached.")
            print("=" * 60)
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"  ✗ Attempt {attempt} failed: {error_msg[:100]}")
            
            if attempt < max_retries:
                wait_time = attempt * 5
                print(f"  → Retrying in {wait_time} seconds...\n")
                import time
                time.sleep(wait_time)
            else:
                print("\n" + "=" * 60)
                print("FAILED: Could not download model after", max_retries, "attempts")
                print("=" * 60)
                print("\nPossible solutions:")
                print("1. Check Windows Firewall - allow Python through firewall")
                print("2. Temporarily disable antivirus and try again")
                print("3. Use a VPN if you're in a restricted network")
                print("4. Try downloading from a different network")
                print("5. Manual download: https://huggingface.co/sshleifer/distilbart-cnn-12-6")
                return False
    
    return False

if __name__ == "__main__":
    success = download_model_with_retry()
    sys.exit(0 if success else 1)

