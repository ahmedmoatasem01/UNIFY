# Quick Start: AI Assistant with Ollama LLM

Transform your AI Assistant from template-based to intelligent LLM-powered responses in **3 steps**!

## Before vs After

### Before (Template-Based)
```
Q: "What are the prerequisites for Machine Learning?"
A: "Machine Learning (CS401) requires Data Structures (CS202)..."
```

### After (LLM-Powered)
```
Q: "What are the prerequisites for Machine Learning?"
A: "To enroll in Machine Learning (CS401), you need to complete three 
    prerequisite courses: Data Structures, Linear Algebra, and Probability 
    & Statistics. The course covers supervised learning, neural networks, 
    and includes a lab component. It's offered in Spring semester only..."
```

**Much more natural and helpful!** 🚀

## Setup in 3 Steps

### Step 1: Install Ollama

**Windows:**
1. Download: https://ollama.ai/download/windows
2. Run the installer
3. Done!

**Verify:**
```powershell
ollama --version
```

### Step 2: Download a Model

**Recommended for beginners (3.8 GB, needs 8 GB RAM):**
```powershell
ollama pull llama2
```

**Better quality (4.1 GB, needs 8 GB RAM):**
```powershell
ollama pull mistral
```

**Lightweight (1.6 GB, needs 4 GB RAM):**
```powershell
ollama pull phi
```

### Step 3: Configure & Run

**Create `.env` file in project root:**
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2
```

**Start the app:**
```powershell
cd c:\Users\Acer\Desktop\Unify\UNIFY
python app.py
```

**That's it!** Navigate to `http://localhost:5000/ai-assistant` 🎉

## How to Use

1. **Open AI Assistant**: `http://localhost:5000/ai-assistant`
2. **Ask questions**: Type naturally like talking to a person
3. **Get intelligent answers**: LLM generates contextual responses
4. **See sources**: Original documents are cited

## Example Questions

Try these to see the difference:

- "Explain the prerequisites for Data Structures course"
- "When is the deadline for course registration and what happens if I miss it?"
- "How is GPA calculated at our university?"
- "What financial aid options are available?"

## Troubleshooting

### "Could not connect to Ollama"

```powershell
# Check if running
ollama list

# If not, start it
ollama serve
```

### "Model not found"

```powershell
# Download the model
ollama pull llama2
```

### "Too slow"

```powershell
# Use a smaller, faster model
ollama pull phi
```

Update `.env`:
```env
OLLAMA_MODEL=phi
```

### "Ollama not installed"

Download from: https://ollama.ai/download

## Advanced Options

### Use Different Models

```powershell
# List available models
ollama list

# Download a model
ollama pull mistral

# Use in app (update .env)
OLLAMA_MODEL=mistral
```

### Use OpenAI Instead

Don't want to run locally? Use OpenAI:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

```powershell
pip install openai
```

### Disable LLM

Want to go back to template-based?

Just remove or comment out in `.env`:
```env
# LLM_PROVIDER=ollama
```

## Model Comparison

| Model | Size | RAM | Speed | Quality |
|-------|------|-----|-------|---------|
| phi | 1.6GB | 4GB | ⚡⚡⚡ | ⭐⭐⭐ |
| llama2 | 3.8GB | 8GB | ⚡⚡ | ⭐⭐⭐⭐ |
| mistral | 4.1GB | 8GB | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| llama2:13b | 7.3GB | 16GB | ⚡ | ⭐⭐⭐⭐⭐ |

**Recommendation**: Start with `llama2`, upgrade to `mistral` if you want better quality.

## Performance Tips

1. **Close other apps** to free up RAM
2. **Use GPU** if available (Ollama auto-detects)
3. **Choose smaller model** for faster responses
4. **Reduce max_tokens** in code for shorter answers

## What Gets Better with LLM?

✅ **Natural language** - Responses sound human  
✅ **Context awareness** - Understands nuance  
✅ **Better explanations** - More detailed and helpful  
✅ **Follow-up questions** - Can elaborate on topics  
✅ **Multiple sources** - Combines info from different docs  

## Files Changed

```
src/
├── services/
│   └── llm_service.py          ← NEW! LLM integration
├── controllers/
│   └── ai_assistant_controller.py  ← Updated to use LLM
└── .env                        ← NEW! Your configuration

OLLAMA_SETUP_GUIDE.md          ← Detailed setup guide
```

## Need More Help?

Read the full guide: `OLLAMA_SETUP_GUIDE.md`

Or check:
- Ollama docs: https://github.com/jmorganca/ollama
- Our AI Assistant docs: `README_AI_ASSISTANT.md`

---

**Enjoy your intelligent AI Assistant!** 🤖✨
