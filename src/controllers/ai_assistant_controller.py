"""
AI Assistant Controller
HTTP request handlers for AI Assistant endpoints
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from repositories.repository_factory import RepositoryFactory
from models.knowledge_base import KnowledgeBase
from models.chat_history import ChatHistory
from services.ai_assistant_service import get_rag_engine
import json

ai_assistant_bp = Blueprint('ai_assistant', __name__, url_prefix='/ai-assistant')

# Initialize repositories
try:
    kb_repo = RepositoryFactory.get_repository('knowledge_base')
    chat_repo = RepositoryFactory.get_repository('chat_history')
    
    # Initialize tables
    kb_repo.create_table()
    chat_repo.create_table()
except Exception as e:
    print(f"Warning: AI Assistant repositories not available: {e}")
    kb_repo = None
    chat_repo = None

# Initialize LLM service
try:
    from services.llm_service import get_llm_service
    llm_service = get_llm_service()
    if llm_service:
        print(f"[AI Assistant] LLM service initialized: {llm_service.provider}")
    else:
        print("[AI Assistant] No LLM available, using template-based responses")
except Exception as e:
    print(f"[AI Assistant] Error initializing LLM service: {e}")
    llm_service = None

# Initialize RAG Engine service
rag_engine = get_rag_engine()


@ai_assistant_bp.route('/')
def index():
    """AI Assistant main page"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_id = session.get('user_id')
    
    # Get recent chat history
    recent_chats = []
    if chat_repo:
        try:
            recent_chats = chat_repo.get_recent_chats(user_id, limit=10)
            recent_chats = [chat.to_dict() for chat in recent_chats]
        except Exception as e:
            print(f"Error loading chat history: {e}")
    
    # Get categories
    categories = []
    if kb_repo:
        try:
            categories = kb_repo.get_categories()
        except Exception as e:
            print(f"Error loading categories: {e}")
    
    return render_template('ai_assistant.html', 
                          recent_chats=recent_chats,
                          categories=categories)


@ai_assistant_bp.route('/ask', methods=['POST'])
def ask_question():
    """Handle user question and generate RAG-based answer"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        question = data.get('question', '').strip()
        selected_model = data.get('model', 'unify')  # Default to 'unify' if not specified
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Get user ID
        user_id = session.get('user_id')
        
        # Retrieve relevant documents from knowledge base
        relevant_docs = rag_engine.retrieve_relevant_docs(question, limit=3)
        
        # Retrieve user-specific context (tasks, schedule, deadlines)
        user_context = None
        if user_id:
            try:
                user_context = rag_engine.retrieve_user_context(user_id)
            except Exception as e:
                print(f"Error retrieving user context: {e}")
        
        # Use LLM service only if user selected 'ollama' and service is available
        # Otherwise use Unify Model (template-based)
        llm_service_to_use = None
        if selected_model == 'ollama' and llm_service:
            llm_service_to_use = llm_service
            print(f"[AI Assistant] Using Ollama model as requested by user")
        else:
            print(f"[AI Assistant] Using Unify Model (template-based)")
        
        # Generate answer with user context
        result = rag_engine.generate_answer(question, relevant_docs, user_context, llm_service_to_use)
        
        # Save to chat history
        if chat_repo:
            try:
                chat_history = ChatHistory(
                    user_id=session.get('user_id'),
                    question=question,
                    answer=result['answer'],
                    sources=json.dumps([s['kb_id'] for s in result['sources']])
                )
                chat_repo.add(chat_history)
            except Exception as e:
                print(f"Error saving chat history: {e}")
        
        return jsonify({
            'success': True,
            'answer': result['answer'],
            'sources': result['sources'],
            'confidence': result['confidence']
        })
    
    except Exception as e:
        print(f"Error in ask_question: {e}")
        return jsonify({'error': str(e)}), 500


@ai_assistant_bp.route('/history', methods=['GET'])
def get_history():
    """Get user's chat history"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session.get('user_id')
        limit = request.args.get('limit', 50, type=int)
        
        if not chat_repo:
            return jsonify({'history': []})
        
        history = chat_repo.get_by_user_id(user_id, limit=limit)
        history_list = [chat.to_dict() for chat in history]
        
        return jsonify({'success': True, 'history': history_list})
    
    except Exception as e:
        print(f"Error getting history: {e}")
        return jsonify({'error': str(e)}), 500


@ai_assistant_bp.route('/clear-history', methods=['POST'])
def clear_history():
    """Clear user's chat history"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        user_id = session.get('user_id')
        
        if chat_repo:
            chat_repo.delete_by_user(user_id)
        
        return jsonify({'success': True, 'message': 'Chat history cleared'})
    
    except Exception as e:
        print(f"Error clearing history: {e}")
        return jsonify({'error': str(e)}), 500


@ai_assistant_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all knowledge base categories"""
    try:
        if not kb_repo:
            return jsonify({'categories': []})
        
        categories = kb_repo.get_categories()
        return jsonify({'success': True, 'categories': categories})
    
    except Exception as e:
        print(f"Error getting categories: {e}")
        return jsonify({'error': str(e)}), 500


@ai_assistant_bp.route('/knowledge-base', methods=['GET'])
def get_knowledge_base():
    """Get all knowledge base documents (admin feature)"""
    try:
        if not kb_repo:
            return jsonify({'documents': []})
        
        category = request.args.get('category')
        
        if category:
            documents = kb_repo.search_by_category(category)
        else:
            documents = kb_repo.get_all()
        
        docs_list = [doc.to_dict() for doc in documents]
        
        return jsonify({'success': True, 'documents': docs_list})
    
    except Exception as e:
        print(f"Error getting knowledge base: {e}")
        return jsonify({'error': str(e)}), 500
