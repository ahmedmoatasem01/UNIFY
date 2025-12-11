# AI Note Summarizer - Model Download Instructions

## Problem
The AI Note Summarizer requires a machine learning model that needs to be downloaded from Hugging Face. If you see an error about not being able to connect to huggingface.co, follow these steps:

## Solution 1: Download Model with Internet Connection

1. **Ensure you have an active internet connection**
2. **Open a terminal/command prompt in the project directory**
3. **Navigate to the src folder:**
   ```bash
   cd UNIFY/src
   ```
4. **Run the download script:**
   ```bash
   python download_model.py
   ```
5. **Wait for the download to complete** (this may take 5-10 minutes depending on your connection)
6. **Once complete, the model will be cached locally and you can use the summarizer offline**

## Solution 2: Manual Download (If Script Fails)

If the script doesn't work, you can manually download the model:

1. **Visit:** https://huggingface.co/sshleifer/distilbart-cnn-12-6
2. **Download all model files** to a local directory
3. **Update the model path in `AI_Note_controller.py`** to point to your local directory

## Solution 3: Use a Different Model (Lighter Alternative)

If you have limited internet or want a smaller model, you can use:

```python
model_name = "facebook/bart-large-cnn"  # Larger but more accurate
# OR
model_name = "google/pegasus-xsum"  # Alternative option
```

## Troubleshooting

### Check Internet Connection
- Open a browser and visit: https://huggingface.co
- If the site doesn't load, check your internet connection or firewall settings

### Check Firewall/Proxy
- Some corporate networks block huggingface.co
- Contact your IT department if you're on a corporate network
- Try using a VPN or different network

### Check Disk Space
- The model requires approximately 500MB of free space
- Ensure you have enough disk space available

### Alternative: Use Without AI (Manual Summaries)
If you cannot download the model, you can still use the notes feature to:
- Upload and store your notes
- View saved notes
- Manually add summaries

The AI summarization feature will be disabled until the model is downloaded.

