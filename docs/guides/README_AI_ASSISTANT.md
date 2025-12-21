# AI Assistant - RAG Implementation

## Overview

The AI Assistant is a **Retrieval-Augmented Generation (RAG)** system that allows users to ask questions and receive answers based on information stored in the knowledge base.

## How It Works

### RAG Architecture

```
User Question → Keyword Extraction → Knowledge Base Search → Relevant Docs Retrieval → Answer Generation → User
```

1. **User asks a question** through the chat interface
2. **Keywords are extracted** from the question
3. **Knowledge base is searched** for relevant documents
4. **Top matching documents** are retrieved
5. **Answer is generated** using the retrieved context
6. **Answer is displayed** with source citations

## Features

✨ **Intelligent Question Answering**
- Natural language question processing
- Context-aware responses
- Source attribution for transparency

📚 **Knowledge Base Management**
- Store documents by category
- Keyword-based search
- Multi-source document retrieval

💬 **Interactive Chat Interface**
- Real-time conversation
- Chat history tracking
- Sample questions for quick start

🎨 **Beautiful UI**
- Modern, responsive design
- Gradient color scheme
- Smooth animations

## Setup Instructions

### 1. Initialize the Knowledge Base

Run the population script to add sample data:

```bash
cd src/utils
python populate_knowledge_base.py
```

This will add sample documents about:
- Course information
- Academic policies
- Campus resources
- Student life
- Technology services
- Financial information

### 2. Access the AI Assistant

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Navigate to: `http://localhost:5000/ai-assistant`

3. Ask questions like:
   - "What are the prerequisites for Data Structures?"
   - "When is the course registration deadline?"
   - "How do I calculate my GPA?"
   - "Where is the library located?"

## File Structure

```
src/
├── controllers/
│   └── ai_assistant_controller.py   # RAG logic and API endpoints
├── models/
│   ├── knowledge_base.py            # Knowledge base document model
│   └── chat_history.py              # Chat history model
├── repositories/
│   ├── knowledge_base.repository.py # Database operations for KB
│   └── chat_history.repository.py   # Database operations for chat
├── templates/
│   └── ai_assistant.html            # Chat interface UI
├── static/
│   ├── styles/
│   │   └── ai_assistant.css         # Styling
│   └── scripts/
│       └── ai_assistant.js          # Frontend logic
└── utils/
    └── populate_knowledge_base.py   # Data population script
```

## Database Schema

### Knowledge_Base Table
```sql
CREATE TABLE Knowledge_Base (
    KB_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    Content TEXT NOT NULL,
    Category TEXT,
    Keywords TEXT,
    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Updated_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Source TEXT
)
```

### Chat_History Table
```sql
CREATE TABLE Chat_History (
    Chat_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    User_ID INTEGER NOT NULL,
    Question TEXT NOT NULL,
    Answer TEXT NOT NULL,
    Sources TEXT,
    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID) REFERENCES Users(User_ID)
)
```

## API Endpoints

### POST `/ai-assistant/ask`
Ask a question and get an AI-generated answer.

**Request:**
```json
{
  "question": "What are the prerequisites for Machine Learning?"
}
```

**Response:**
```json
{
  "success": true,
  "answer": "Machine Learning (CS401) requires...",
  "sources": [
    {
      "kb_id": 3,
      "title": "Machine Learning Course (CS401)",
      "category": "Courses",
      "excerpt": "Machine Learning (CS401) introduces..."
    }
  ],
  "confidence": "high"
}
```

### GET `/ai-assistant/history`
Get user's chat history.

**Response:**
```json
{
  "success": true,
  "history": [
    {
      "Chat_ID": 1,
      "User_ID": 1,
      "Question": "What is...",
      "Answer": "...",
      "Created_Date": "2025-12-21 10:30:00"
    }
  ]
}
```

### POST `/ai-assistant/clear-history`
Clear user's chat history.

**Response:**
```json
{
  "success": true,
  "message": "Chat history cleared"
}
```

## RAG Implementation Details

### Retrieval Strategy

The system uses **keyword-based retrieval**:

1. Extract keywords from the question (removing stop words)
2. Search the knowledge base for documents matching keywords
3. Rank results by relevance:
   - Title matches (highest priority)
   - Keyword matches (medium priority)
   - Content matches (lower priority)
4. Return top 3 most relevant documents

### Answer Generation

The system uses a **template-based approach** that:

1. Analyzes the question type (what, how, when, where, who)
2. Selects an appropriate response template
3. Combines information from retrieved documents
4. Formats the answer with proper structure
5. Adds source citations

### Confidence Scoring

Confidence levels are determined by:
- **High**: 2+ relevant documents found
- **Medium**: 1 relevant document found
- **Low**: No relevant documents found

## Upgrading to Advanced RAG

To enhance the system with AI models:

### Option 1: OpenAI API

```python
import openai

def generate_answer_with_gpt(query, relevant_docs):
    context = "\n\n".join([doc.Content for doc in relevant_docs])
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful university assistant."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
    )
    
    return response.choices[0].message.content
```

### Option 2: Hugging Face (Local Model)

```python
from transformers import pipeline

qa_pipeline = pipeline("question-answering")

def generate_answer_with_hf(query, relevant_docs):
    context = " ".join([doc.Content for doc in relevant_docs])
    result = qa_pipeline(question=query, context=context)
    return result['answer']
```

### Option 3: Sentence Transformers (Vector Search)

```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def vector_search(query, documents):
    query_embedding = model.encode(query)
    doc_embeddings = model.encode([doc.Content for doc in documents])
    similarities = util.cos_sim(query_embedding, doc_embeddings)[0]
    
    # Return top matches
    top_indices = similarities.argsort(descending=True)[:3]
    return [documents[i] for i in top_indices]
```

## Adding New Knowledge

To add new documents to the knowledge base:

```python
from repositories.repository_factory import RepositoryFactory
from models.knowledge_base import KnowledgeBase

kb_repo = RepositoryFactory.get_repository('knowledge_base')

new_doc = KnowledgeBase(
    title="New Document Title",
    content="Full document content...",
    category="Category Name",
    keywords="keyword1, keyword2, keyword3",
    source="Source Name"
)

kb_repo.add(new_doc)
```

## Categories

Current knowledge base categories:
- Academic Programs
- Courses
- Academic Policies
- Campus Resources
- Student Life
- Technology
- Financial

## Troubleshooting

### Issue: No answers returned
**Solution**: Make sure the knowledge base is populated:
```bash
python src/utils/populate_knowledge_base.py
```

### Issue: Database errors
**Solution**: Check if tables are created:
```python
kb_repo = RepositoryFactory.get_repository('knowledge_base')
kb_repo.create_table()

chat_repo = RepositoryFactory.get_repository('chat_history')
chat_repo.create_table()
```

### Issue: Search not finding relevant documents
**Solution**: Add more keywords to your documents or improve the search query.

## Future Enhancements

Potential improvements:

1. **Vector-based search** using embeddings
2. **LLM integration** (OpenAI, Llama, etc.)
3. **Multi-turn conversations** with context memory
4. **File upload** for knowledge base expansion
5. **Admin panel** for knowledge base management
6. **Export chat history** as PDF/text
7. **Voice input/output** capabilities
8. **Multilingual support**

## Contributing

To add new features or improve the RAG system:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

Part of the Unify Student Portal system.

---

**Questions or Issues?**
Contact the development team or open an issue on the project repository.
