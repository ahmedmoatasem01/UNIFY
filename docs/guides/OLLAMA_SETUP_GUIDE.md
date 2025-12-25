# Ollama Setup Guide for AI Assistant

## What is Ollama?

**Ollama** is a tool that lets you run large language models (LLMs) locally on your computer. No API keys, no internet required, completely free!

### Benefits:
✅ **Free** - No API costs  
✅ **Private** - Data stays on your computer  
✅ **Fast** - No network latency  
✅ **Offline** - Works without internet  
✅ **Multiple Models** - Llama2, Mistral, CodeLlama, and more  

## Installation (Windows)

### Step 1: Download Ollama

Visit: **https://ollama.ai/download/windows**

Or direct download: **https://ollama.ai/download/OllamaSetup.exe**

### Step 2: Install Ollama

1. Run `OllamaSetup.exe`
2. Follow the installation wizard
3. Ollama will install to `C:\Users\<YourName>\AppData\Local\Programs\Ollama`

### Step 3: Verify Installation

Open PowerShell and run:

```powershell
ollama --version
```

You should see something like: `ollama version 0.1.17`

## Download a Model

Ollama supports many models. Here are the recommended ones:

### Llama 2 (Recommended for beginners)
```powershell
ollama pull llama2
```
- **Size**: ~3.8 GB
- **RAM**: 8 GB minimum
- **Speed**: Fast
- **Quality**: Good

### Mistral (Better quality, larger)
```powershell
ollama pull mistral
```
- **Size**: ~4.1 GB
- **RAM**: 8 GB minimum
- **Speed**: Fast
- **Quality**: Excellent

### Llama 2 13B (Higher quality, needs more RAM)
```powershell
ollama pull llama2:13b
```
- **Size**: ~7.3 GB
- **RAM**: 16 GB minimum
- **Speed**: Medium
- **Quality**: Excellent

### Code Llama (For code-related questions)
```powershell
ollama pull codellama
```
- **Size**: ~3.8 GB
- **RAM**: 8 GB minimum
- **Speed**: Fast
- **Quality**: Good for coding

## Start Ollama Server

### Option 1: Auto-start (Recommended)

Ollama starts automatically on Windows. Check if it's running:

```powershell
ollama list
```

### Option 2: Manual Start

If not running, start it manually:

```powershell
ollama serve
```

Keep this terminal window open!

## Test Ollama

### Test in Terminal

```powershell
ollama run llama2
```

Type a question:
```
>>> What is machine learning?
```

Press `Ctrl+D` or type `/bye` to exit.

### Test with Python

Create a test file `test_ollama.py`:

```python
import requests
import json

url = "http://localhost:11434/api/generate"

payload = {
    "model": "llama2",
    "prompt": "What is Python? Answer in one sentence.",
    "stream": False
}

response = requests.post(url, json=payload)
result = response.json()
print(result['response'])
```

Run it:
```powershell
python test_ollama.py
```

## Configure for Unify Application

### Step 1: Create .env File

In your project root (`c:\Users\Acer\Desktop\Unify\UNIFY\`), create a `.env` file:

```env
# Enable LLM
LLM_PROVIDER=ollama

# Ollama Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Optional: Enable multi-tenant mode
MULTI_TENANT_MODE=false
```

### Step 2: Install Python Dependencies

```powershell
cd c:\Users\Acer\Desktop\Unify\UNIFY
pip install requests
```

### Step 3: Test Integration

```powershell
cd src\services
python llm_service.py
```

You should see:
```
Testing LLM Service...
------------------------------------------------------------

1. Testing Ollama connection...
✓ Ollama is available
  Available models: llama2, ...

2. Testing text generation...
  Response: Machine learning is a type of artificial intelligence...
```

### Step 4: Start Your Application

```powershell
python app.py
```

The AI Assistant will now use Ollama for responses!

## Using the AI Assistant with LLM

1. **Start the application**:
   ```powershell
   python app.py
   ```

2. **Navigate to**: `http://localhost:5000/ai-assistant`

3. **Ask questions**:
   - "What are the prerequisites for Data Structures?"
   - "When is course registration?"
   - "How do I calculate my GPA?"

4. **See the difference**:
   - **Without LLM**: Template-based, simple responses
   - **With LLM**: Intelligent, contextual, natural responses

## Available Models

### Small Models (4-8 GB RAM)
```powershell
ollama pull llama2           # 3.8 GB - General purpose
ollama pull mistral          # 4.1 GB - Better quality
ollama pull phi              # 1.6 GB - Very small, fast
ollama pull orca-mini        # 1.9 GB - Small, efficient
```

### Medium Models (16 GB RAM)
```powershell
ollama pull llama2:13b       # 7.3 GB - Higher quality
ollama pull codellama:13b    # 7.3 GB - Better for code
ollama pull vicuna:13b       # 7.3 GB - Good conversations
```

### Large Models (32 GB RAM)
```powershell
ollama pull llama2:70b       # 39 GB - Best quality
ollama pull codellama:34b    # 19 GB - Professional coding
```

## Switch Models

### In Terminal:
```powershell
ollama run mistral
```

### In Application:

Update your `.env` file:
```env
OLLAMA_MODEL=mistral
```

Restart the application.

## Troubleshooting

### Issue: "Could not connect to Ollama"

**Solution 1**: Check if Ollama is running
```powershell
ollama list
```

**Solution 2**: Start Ollama server
```powershell
ollama serve
```

**Solution 3**: Check if port 11434 is in use
```powershell
netstat -ano | findstr :11434
```

### Issue: "Model not found"

**Solution**: Pull the model first
```powershell
ollama pull llama2
```

### Issue: "Response too slow"

**Solution 1**: Use a smaller model
```powershell
ollama pull phi
```

**Solution 2**: Increase timeout in code
```python
# In llm_service.py
response = requests.post(url, json=payload, timeout=120)  # Increase from 60 to 120
```

**Solution 3**: Reduce max_tokens
```python
llm.max_tokens = 500  # Reduce from 1000
```

### Issue: "Out of memory"

**Solution 1**: Use a smaller model
```powershell
ollama pull phi  # Only 1.6 GB
```

**Solution 2**: Close other applications

**Solution 3**: Upgrade RAM (recommended: 16 GB)

### Issue: "Incorrect answers"

**Solution 1**: Use a better model
```powershell
ollama pull mistral  # Better than llama2
```

**Solution 2**: Adjust temperature in code
```python
# In llm_service.py
self.temperature = 0.3  # Lower = more focused, Higher = more creative
```

**Solution 3**: Add more context to knowledge base
```powershell
python src\utils\populate_knowledge_base.py
```

## Performance Optimization

### 1. Use GPU Acceleration (if available)

Ollama automatically uses GPU if available. Check:
```powershell
ollama run llama2
# If GPU is used, you'll see: "loaded on GPU"
```

### 2. Adjust Model Parameters

In `llm_service.py`, modify:

```python
# Faster but less quality
self.max_tokens = 500
self.temperature = 0.5

# Slower but better quality
self.max_tokens = 2000
self.temperature = 0.7
```

### 3. Cache Responses

The application already caches in chat history. Users can see previous answers instantly!

## Advanced Configuration

### Custom System Prompts

In `llm_service.py`, modify the system prompt:

```python
system_prompt = (
    "You are a knowledgeable university assistant specializing in "
    "Computer Science at Zewail City. "
    "Provide accurate, concise answers based on the provided documents. "
    "Always cite sources when available."
)
```

### Multiple Model Support

Configure different models for different tasks:

```python
# In llm_service.py
if "code" in question.lower():
    llm = LLMService(provider='ollama', model='codellama')
elif "math" in question.lower():
    llm = LLMService(provider='ollama', model='mistral')
else:
    llm = LLMService(provider='ollama', model='llama2')
```

## Comparison: Template vs LLM

### Template-Based (Default without Ollama)

**Question**: "What are the prerequisites for Machine Learning?"

**Answer**:
```
Based on the information available:

**Machine Learning Course (CS401)**
Machine Learning (CS401) introduces fundamental concepts and algorithms in machine learning.

Prerequisites: Data Structures (CS202), Linear Algebra (MATH201), Probability and Statistics (MATH301)
```

### LLM-Based (With Ollama)

**Question**: "What are the prerequisites for Machine Learning?"

**Answer**:
```
To enroll in Machine Learning (CS401) at Zewail City, you need to complete 
three prerequisite courses:

1. **Data Structures (CS202)** - This foundational computer science course 
   covers essential data structures needed for implementing ML algorithms.

2. **Linear Algebra (MATH201)** - Mathematical foundation for understanding 
   matrices, vectors, and transformations used extensively in machine learning.

3. **Probability and Statistics (MATH301)** - Essential for understanding 
   probabilistic models, statistical inference, and model evaluation.

The course is offered only in the Spring semester and includes a lab component. 
It's worth 3 credit hours and covers topics including supervised learning, 
unsupervised learning, neural networks, and real-world applications.
```

**Notice the difference?**
- More natural language
- Better structure and organization  
- Additional context and explanations
- More helpful and comprehensive

## Cloud Alternatives (if local doesn't work)

If your computer can't run Ollama, use cloud services:

### OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

```powershell
pip install openai
```

### Anthropic (Claude)

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=claude-2
```

```powershell
pip install anthropic
```

## Best Practices

1. **Start Small**: Begin with `llama2`, upgrade to `mistral` if needed
2. **Monitor RAM**: Keep Task Manager open to watch memory usage
3. **Test Locally**: Test questions in terminal before using in app
4. **Update Regularly**: Run `ollama update` to get latest improvements
5. **Read Docs**: Visit https://github.com/jmorganca/ollama for more info

## Resources

- **Ollama Website**: https://ollama.ai
- **Ollama GitHub**: https://github.com/jmorganca/ollama
- **Model Library**: https://ollama.ai/library
- **Community Discord**: https://discord.gg/ollama
- **Documentation**: https://github.com/jmorganca/ollama/tree/main/docs

## Need Help?

1. Check Ollama logs:
   ```powershell
   ollama logs
   ```

2. Restart Ollama:
   ```powershell
   # Stop
   taskkill /F /IM ollama.exe
   
   # Start
   ollama serve
   ```

3. Reinstall model:
   ```powershell
   ollama rm llama2
   ollama pull llama2
   ```

4. Check application logs:
   ```powershell
   python app.py
   # Watch for [LLM] and [RAG] messages
   ```

---

**Ready to go!** Your AI Assistant is now powered by local LLM! 🚀
