"""
Unit tests for LLM Service
Tests LLM service functionality including model detection and response generation
"""
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from services.llm_service import LLMService, get_llm_service


class TestLLMService(unittest.TestCase):
    """Test cases for LLM Service"""
    
    def test_llm_service_initialization_default(self):
        """Test LLM Service initializes with default settings"""
        with patch('services.llm_service.requests') as mock_requests:
            # Mock Ollama API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'models': [
                    {'name': 'llama3:latest'},
                    {'name': 'phi:latest'}
                ]
            }
            mock_requests.get.return_value = mock_response
            
            service = LLMService(provider='ollama')
            
            # Verify initialization
            self.assertEqual(service.provider, 'ollama')
            self.assertIsNotNone(service.model)
            self.assertEqual(service.ollama_url, 'http://localhost:11434')
    
    def test_llm_service_auto_detects_models(self):
        """Test that LLM Service auto-detects available Ollama models"""
        with patch('services.llm_service.requests') as mock_requests:
            # Mock Ollama API response with multiple models
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'models': [
                    {'name': 'llama3:latest'},
                    {'name': 'mistral:latest'},
                    {'name': 'phi:latest'}
                ]
            }
            mock_requests.get.return_value = mock_response
            
            service = LLMService(provider='ollama')
            
            # Verify it prefers llama3
            self.assertIn('llama3', service.model.lower())
    
    def test_llm_service_is_available_check(self):
        """Test that is_available correctly checks Ollama availability"""
        with patch('services.llm_service.requests') as mock_requests:
            # Test available
            mock_response = Mock()
            mock_response.status_code = 200
            mock_requests.get.return_value = mock_response
            
            service = LLMService(provider='ollama')
            self.assertTrue(service.is_available())
            
            # Test unavailable
            mock_requests.get.side_effect = Exception("Connection error")
            self.assertFalse(service.is_available())
    
    def test_llm_service_list_available_models(self):
        """Test that list_available_models returns list of models"""
        with patch('services.llm_service.requests') as mock_requests:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'models': [
                    {'name': 'llama3:latest'},
                    {'name': 'mistral:latest'}
                ]
            }
            mock_requests.get.return_value = mock_response
            
            service = LLMService(provider='ollama')
            models = service.list_available_models()
            
            # Verify models are listed
            self.assertIsInstance(models, list)
            self.assertGreater(len(models), 0)
            self.assertIn('llama3:latest', models)
    
    def test_llm_service_generate_rag_response(self):
        """Test that generate_rag_response creates proper RAG responses"""
        # Create mock documents
        mock_doc1 = Mock()
        mock_doc1.Title = "Document 1"
        mock_doc1.Category = "Courses"
        mock_doc1.Content = "Content about data structures"
        
        mock_doc2 = Mock()
        mock_doc2.Title = "Document 2"
        mock_doc2.Category = "Policies"
        mock_doc2.Content = "Content about academic policies"
        
        with patch('services.llm_service.requests') as mock_requests:
            # Mock Ollama API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'models': [{'name': 'llama3:latest'}]
            }
            mock_requests.get.return_value = mock_response
            
            service = LLMService(provider='ollama')
            
            # Mock generate method
            service.generate = Mock(return_value="This is a generated answer about data structures.")
            
            # Test RAG response
            result = service.generate_rag_response(
                question="What are data structures?",
                retrieved_docs=[mock_doc1, mock_doc2]
            )
            
            # Verify result structure
            self.assertIsInstance(result, dict)
            self.assertIn('answer', result)
            self.assertIn('confidence', result)
            self.assertGreater(len(result['answer']), 0)
            self.assertIn(result['confidence'], ['high', 'medium', 'low'])
    
    def test_llm_service_handles_empty_documents(self):
        """Test that generate_rag_response handles empty document list"""
        with patch('services.llm_service.requests') as mock_requests:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'models': []}
            mock_requests.get.return_value = mock_response
            
            service = LLMService(provider='ollama')
            result = service.generate_rag_response(
                question="test question",
                retrieved_docs=[]
            )
            
            # Verify it handles empty docs gracefully
            self.assertIsInstance(result, dict)
            self.assertIn('answer', result)
            self.assertIn('confidence', result)
            self.assertEqual(result['confidence'], 'low')
    
    def test_get_llm_service_returns_service_when_available(self):
        """Test that get_llm_service returns service when Ollama is available"""
        with patch('services.llm_service.requests') as mock_requests:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'models': [{'name': 'llama3:latest'}]
            }
            mock_requests.get.return_value = mock_response
            
            service = get_llm_service()
            
            # Verify service is returned
            self.assertIsNotNone(service)
            self.assertEqual(service.provider, 'ollama')
    
    def test_get_llm_service_returns_none_when_unavailable(self):
        """Test that get_llm_service returns None when no LLM is available"""
        with patch('services.llm_service.requests') as mock_requests:
            # Mock connection error
            mock_requests.get.side_effect = Exception("Connection failed")
            
            service = get_llm_service()
            
            # Verify None is returned
            self.assertIsNone(service)


if __name__ == '__main__':
    unittest.main()
