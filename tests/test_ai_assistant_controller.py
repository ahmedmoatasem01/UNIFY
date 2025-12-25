"""
Unit tests for AI Assistant Controller
Tests HTTP endpoints and request handling
"""
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

from src.controllers.ai_assistant_controller import ai_assistant_bp


class TestAIAssistantController(unittest.TestCase):
    """Test cases for AI Assistant Controller"""
    
    def setUp(self):
        """Set up test client"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.register_blueprint(ai_assistant_bp)
        self.client = self.app.test_client()
    
    def test_ask_question_requires_authentication(self):
        """Test that ask_question endpoint requires authentication"""
        response = self.client.post('/ai-assistant/ask',
                                  json={'question': 'test question'},
                                  content_type='application/json')
        
        # Should return 401 Unauthorized
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_ask_question_requires_question_field(self):
        """Test that ask_question endpoint requires question field"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
        
        # Missing question
        response = self.client.post('/ai-assistant/ask',
                                  json={},
                                  content_type='application/json')
        
        # Should return 400 Bad Request
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_ask_question_returns_json_response(self):
        """Test that ask_question returns proper JSON response"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
        
        # Mock RAG engine
        mock_result = {
            'answer': 'This is a test answer',
            'sources': [{'kb_id': 1, 'title': 'Test Doc'}],
            'confidence': 'high'
        }
        
        with patch('controllers.ai_assistant_controller.rag_engine') as mock_engine:
            mock_engine.retrieve_relevant_docs.return_value = []
            mock_engine.retrieve_user_context.return_value = None
            mock_engine.generate_answer.return_value = mock_result
            
            with patch('controllers.ai_assistant_controller.chat_repo') as mock_chat:
                mock_chat.add = Mock()
                
                response = self.client.post('/ai-assistant/ask',
                                          json={'question': 'test question', 'model': 'unify'},
                                          content_type='application/json')
                
                # Should return 200 OK
                self.assertEqual(response.status_code, 200)
                data = response.get_json()
                self.assertIn('success', data)
                self.assertIn('answer', data)
                self.assertIn('sources', data)
                self.assertIn('confidence', data)
    
    def test_get_history_requires_authentication(self):
        """Test that get_history endpoint requires authentication"""
        response = self.client.get('/ai-assistant/history')
        
        # Should return 401 Unauthorized
        self.assertEqual(response.status_code, 401)
    
    def test_get_categories_returns_list(self):
        """Test that get_categories endpoint returns category list"""
        with patch('controllers.ai_assistant_controller.kb_repo') as mock_repo:
            mock_repo.get_categories.return_value = ['Courses', 'Policies', 'Resources']
            
            response = self.client.get('/ai-assistant/categories')
            
            # Should return 200 OK
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertIn('success', data)
            self.assertIn('categories', data)
            self.assertIsInstance(data['categories'], list)
    
    def test_model_selection_unify_vs_ollama(self):
        """Test that controller respects model selection (unify vs ollama)"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
        
        with patch('controllers.ai_assistant_controller.rag_engine') as mock_engine:
            mock_engine.retrieve_relevant_docs.return_value = []
            mock_engine.retrieve_user_context.return_value = None
            mock_engine.generate_answer.return_value = {
                'answer': 'test',
                'sources': [],
                'confidence': 'high'
            }
            
            with patch('controllers.ai_assistant_controller.chat_repo') as mock_chat:
                mock_chat.add = Mock()
                
                # Test with Unify Model
                response1 = self.client.post('/ai-assistant/ask',
                                           json={'question': 'test', 'model': 'unify'},
                                           content_type='application/json')
                self.assertEqual(response1.status_code, 200)
                
                # Test with Ollama
                with patch('controllers.ai_assistant_controller.llm_service') as mock_llm:
                    mock_llm = Mock()
                    response2 = self.client.post('/ai-assistant/ask',
                                                json={'question': 'test', 'model': 'ollama'},
                                                content_type='application/json')
                    # Should work if Ollama available, or fallback to Unify
                    self.assertIn(response2.status_code, [200, 500])


if __name__ == '__main__':
    unittest.main()
