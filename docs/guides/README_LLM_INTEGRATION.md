# LLM Integration for AI Assistant

## Overview

The AI Assistant now supports **Large Language Models (LLMs)** for generating intelligent, contextual responses. You can use:

1. **Ollama** (local, free, private)
2. **OpenAI** (cloud, paid, high quality)
3. **Anthropic Claude** (cloud, paid, excellent)
4. **Template-based** (fallback, no setup needed)

## Architecture

```
User Question
    ↓
Keyword Extraction
    ↓
Knowledge Base Search → Retrieve Top 3 Documents
    ↓
LLM Service (Ollama/OpenAI/Claude)
    ↓
Generate Contextual Answer
    ↓
Return with Source Citations
```

## Quick Setup

### Option 1: Ollama (Recommended - Local & Free)

**Install:**
```powershell
# Download and install from https://ollama.ai/download
ollama --version
```

**Download model:**
```powershell
ollama pull llama2
```

**Configure:**
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2
```

### Option 2: OpenAI

**Configure:**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

**Install:**
```powershell
pip install openai
```

### Option 3: Anthropic Claude

**Configure:**
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=claude-2
```

**Install:**
```powershell
pip install anthropic
```

## LLM Service Architecture

### Core Components

**`llm_service.py`** - Unified interface for all LLM providers

```python
from services.llm_service import LLMService

# Initialize
llm = LLMService(provider='ollama', model='llama2')

# Generate text
response = llm.generate(
    prompt="What is machine learning?",
    context="ML is a subset of AI...",
    system_prompt="You are a helpful assistant"
)

# RAG-specific generation
result = llm.generate_rag_response(
    question="What are prerequisites?",
    retrieved_docs=[doc1, doc2, doc3]
)
```

### Provider Support

| Provider | Local/Cloud | Cost | Setup Difficulty | Quality |
|----------|-------------|------|------------------|---------|
| Ollama | Local | Free | Easy | Good |
| OpenAI | Cloud | Paid | Very Easy | Excellent |
| Anthropic | Cloud | Paid | Very Easy | Excellent |
| Template | Local | Free | None | Basic |

## How It Works

### 1. Retrieval Phase

```python
# Extract keywords
keywords = ["machine", "learning", "prerequisites"]

# Search knowledge base
docs = kb_repo.search("machine learning", limit=3)
# Returns: [CS401 doc, CS202 doc, Prerequisites doc]
```

### 2. Generation Phase

**Without LLM (Template-Based):**
```python
answer = "Based on the information available:\n\n"
answer += f"**{docs[0].Title}**\n{docs[0].Content}"
```

**With LLM (Intelligent):**
```python
# Build context from retrieved docs
context = "\n".join([doc.Content for doc in docs])

# Generate with LLM
answer = llm.generate(
    prompt=user_question,
    context=context,
    system_prompt="You are a university assistant..."
)
```

### 3. Response Phase

```json
{
  "answer": "To enroll in Machine Learning (CS401)...",
  "sources": [
    {
      "kb_id": 3,
      "title": "Machine Learning Course",
      "category": "Courses",
      "excerpt": "Prerequisites: CS202, MATH201..."
    }
  ],
  "confidence": "high"
}
```

## Configuration Options

### Basic Configuration

```python
# In llm_service.py
llm = LLMService(
    provider='ollama',      # Provider to use
    model='llama2',         # Model name
    api_key=None           # API key (if needed)
)

# Adjust parameters
llm.temperature = 0.7      # 0.0-1.0 (lower = more focused)
llm.max_tokens = 1000      # Maximum response length
llm.ollama_url = 'http://localhost:11434'  # Ollama server
```

### Advanced Configuration

```python
# Custom system prompts
system_prompt = """
You are an expert academic advisor at Zewail City University.
Provide accurate, helpful information about courses and policies.
Always cite your sources and be concise.
"""

# Custom RAG prompt template
def build_rag_prompt(question, docs):
    context = "\n\n".join([
        f"**Document {i}: {doc.Title}**\n{doc.Content}"
        for i, doc in enumerate(docs, 1)
    ])
    
    return f"""
[SYSTEM]
You are a university assistant. Answer based on the documents below.

[DOCUMENTS]
{context}

[QUESTION]
{question}

[ANSWER]
"""
```

## API Reference

### LLMService Class

#### `__init__(provider, model, api_key)`

Initialize LLM service.

**Parameters:**
- `provider` (str): 'ollama', 'openai', or 'anthropic'
- `model` (str): Model name (e.g., 'llama2', 'gpt-3.5-turbo')
- `api_key` (str): API key for cloud providers

#### `generate(prompt, context, system_prompt)`

Generate text response.

**Parameters:**
- `prompt` (str): User's question
- `context` (str): Additional context
- `system_prompt` (str): System instructions

**Returns:** Generated text (str)

#### `generate_rag_response(question, retrieved_docs)`

Generate RAG response with citations.

**Parameters:**
- `question` (str): User's question
- `retrieved_docs` (list): List of KnowledgeBase objects

**Returns:** Dict with 'answer' and 'confidence'

#### `is_available()`

Check if service is ready.

**Returns:** Boolean

#### `list_available_models()`

List available models (Ollama only).

**Returns:** List of model names

#### `pull_model(model_name)`

Download a model (Ollama only).

**Parameters:**
- `model_name` (str): Model to download

**Returns:** Boolean success

### Helper Functions

#### `get_llm_service(provider, model)`

Auto-configure and return best available LLM service.

**Returns:** LLMService instance or None

## Error Handling

### Connection Errors

```python
try:
    response = llm.generate(prompt)
except ConnectionError as e:
    # Ollama not running
    print("Ollama not available, using template-based")
    response = template_generate(prompt)
```

### Timeout Errors

```python
try:
    response = llm.generate(prompt)
except TimeoutError as e:
    # Request took too long
    print("LLM timeout, using shorter prompt")
```

### Fallback Strategy

```python
# In ai_assistant_controller.py
if llm_service:
    try:
        # Try LLM first
        result = llm_service.generate_rag_response(query, docs)
        answer = result['answer']
    except Exception as e:
        print(f"LLM error: {e}")
        # Fallback to template
        answer = template_generate(query, docs)
else:
    # No LLM available
    answer = template_generate(query, docs)
```

## Performance Optimization

### 1. Caching

```python
# Cache LLM service instance
_llm_cache = None

def get_cached_llm():
    global _llm_cache
    if _llm_cache is None:
        _llm_cache = get_llm_service()
    return _llm_cache
```

### 2. Request Batching

```python
# Process multiple questions together
def batch_generate(questions):
    llm = get_llm_service()
    responses = []
    
    for q in questions:
        docs = retrieve_docs(q)
        resp = llm.generate_rag_response(q, docs)
        responses.append(resp)
    
    return responses
```

### 3. Async Processing

```python
import asyncio

async def async_generate(question):
    docs = await retrieve_docs(question)
    response = await llm.generate_rag_response_async(question, docs)
    return response
```

## Monitoring & Logging

### Enable Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('llm_service')

# In llm_service.py
logger.info(f"Using {self.provider} with model {self.model}")
logger.debug(f"Generating response for: {prompt[:50]}...")
logger.info(f"Generated {len(response)} characters")
```

### Track Usage

```python
class LLMUsageTracker:
    def __init__(self):
        self.requests = 0
        self.total_tokens = 0
        self.errors = 0
    
    def track_request(self, tokens):
        self.requests += 1
        self.total_tokens += tokens
    
    def track_error(self):
        self.errors += 1

tracker = LLMUsageTracker()
```

## Cost Estimation

### OpenAI Costs (as of 2024)

| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|------------------------|
| GPT-3.5 Turbo | $0.0015 | $0.002 |
| GPT-4 | $0.03 | $0.06 |

**Example**: 100 questions/day with GPT-3.5:
- Average: 500 input + 300 output tokens per question
- Cost: (500 × $0.0015 + 300 × $0.002) × 100 = $135/month

### Ollama Costs

**Free!** Only hardware costs:
- Electricity: ~$0.01/hour (depending on GPU)
- No API fees
- No usage limits

## Security Considerations

### API Key Storage

```python
# Never hardcode API keys
# Use environment variables
import os

api_key = os.environ.get('OPENAI_API_KEY')

# Or use secrets management
from cryptography.fernet import Fernet

def encrypt_key(key):
    cipher = Fernet(Fernet.generate_key())
    return cipher.encrypt(key.encode())
```

### Data Privacy

**Ollama (Local)**:
- ✅ Data stays on your computer
- ✅ No external requests
- ✅ Complete privacy

**Cloud Providers**:
- ⚠️ Data sent to third parties
- ⚠️ Subject to provider's privacy policy
- ⚠️ May be used for training (check terms)

## Testing

### Unit Tests

```python
# test_llm_service.py
def test_ollama_connection():
    llm = LLMService(provider='ollama')
    assert llm.is_available()

def test_generate():
    llm = LLMService(provider='ollama')
    response = llm.generate("What is 2+2?")
    assert response is not None
    assert len(response) > 0

def test_rag_response():
    llm = LLMService(provider='ollama')
    docs = [create_test_doc()]
    result = llm.generate_rag_response("Test?", docs)
    assert 'answer' in result
    assert 'confidence' in result
```

### Integration Tests

```python
def test_end_to_end():
    # Ask question
    response = client.post('/ai-assistant/ask', json={
        'question': 'What are prerequisites for CS202?'
    })
    
    # Check response
    assert response.status_code == 200
    data = response.json
    assert 'answer' in data
    assert 'sources' in data
    assert len(data['sources']) > 0
```

## Troubleshooting

### Common Issues

**1. LLM not responding**
```python
# Check if service is available
if not llm.is_available():
    print("LLM service not available")
    # Check logs
    # Verify configuration
```

**2. Poor quality responses**
```python
# Adjust temperature (lower = more focused)
llm.temperature = 0.3

# Use better model
llm.model = 'mistral'  # Instead of llama2

# Improve prompts
system_prompt = "Be very specific and cite sources..."
```

**3. Slow responses**
```python
# Reduce max tokens
llm.max_tokens = 500

# Use smaller model
llm.model = 'phi'

# Increase timeout
response = requests.post(url, timeout=120)
```

## Migration Guide

### From Template to LLM

**Before:**
```python
def generate_answer(query, docs):
    answer = f"Based on {docs[0].Title}:\n{docs[0].Content}"
    return answer
```

**After:**
```python
def generate_answer(query, docs):
    llm = get_llm_service()
    if llm:
        return llm.generate_rag_response(query, docs)
    else:
        # Fallback to template
        return template_generate(query, docs)
```

## Best Practices

1. **Always have fallback** to template-based generation
2. **Cache LLM service** instance, don't recreate
3. **Set reasonable timeouts** (30-60 seconds)
4. **Monitor usage** and costs
5. **Test with different models** to find best fit
6. **Use specific prompts** for better results
7. **Validate responses** before returning to user
8. **Log errors** for debugging

## Future Enhancements

Potential improvements:

1. **Streaming responses** - Show text as it generates
2. **Multi-turn conversations** - Remember context
3. **Model fine-tuning** - Train on university-specific data
4. **Hybrid search** - Combine keyword + semantic search
5. **Answer validation** - Verify accuracy against sources
6. **User feedback** - Learn from thumbs up/down

## Resources

- **Ollama**: https://ollama.ai
- **OpenAI**: https://platform.openai.com/docs
- **Anthropic**: https://docs.anthropic.com
- **LangChain**: https://langchain.com (for advanced RAG)

---

**Questions?** Check `OLLAMA_SETUP_GUIDE.md` or `QUICKSTART_LLM.md`
