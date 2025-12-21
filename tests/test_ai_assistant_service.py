"""
Unit tests for AI Assistant Service (RAG Engine)
Tests the core RAG functionality including document retrieval and answer generation
"""
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from services.ai_assistant_service import RAGEngine, get_rag_engine


class TestRAGEngine(unittest.TestCase):
    """Test cases for RAG Engine service"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock repository
        self.mock_kb_repo = Mock()
        self.mock_kb_repo.search.return_value = []
        
        # Create RAG engine with mocked repository
        with patch('services.ai_assistant_service.RepositoryFactory') as mock_factory:
            mock_factory.get_repository.return_value = self.mock_kb_repo
            self.rag_engine = RAGEngine()
            self.rag_engine.kb_repo = self.mock_kb_repo
    
    def test_retrieve_relevant_docs_with_keywords(self):
        """Test that retrieve_relevant_docs extracts keywords and searches knowledge base"""
        # Create mock documents
        mock_doc1 = Mock()
        mock_doc1.KB_ID = 1
        mock_doc1.Title = "Data Structures"
        mock_doc1.Content = "Data Structures course information"
        
        mock_doc2 = Mock()
        mock_doc2.KB_ID = 2
        mock_doc2.Title = "Algorithms"
        mock_doc2.Content = "Algorithms course information"
        
        # Mock repository search
        self.mock_kb_repo.search.return_value = [mock_doc1, mock_doc2]
        
        # Test retrieval
        query = "What are data structures?"
        docs = self.rag_engine.retrieve_relevant_docs(query, limit=3)
        
        # Verify
        self.assertIsInstance(docs, list)
        self.assertGreater(len(docs), 0)
        self.mock_kb_repo.search.assert_called()
    
    def test_retrieve_relevant_docs_removes_duplicates(self):
        """Test that retrieve_relevant_docs removes duplicate documents"""
        # Create mock documents with duplicate IDs
        mock_doc1 = Mock()
        mock_doc1.KB_ID = 1
        mock_doc1.Title = "Data Structures"
        
        mock_doc2 = Mock()
        mock_doc2.KB_ID = 1  # Duplicate ID
        mock_doc2.Title = "Data Structures"
        
        # Mock repository to return duplicates
        self.mock_kb_repo.search.return_value = [mock_doc1, mock_doc2]
        
        # Test retrieval
        query = "data structures"
        docs = self.rag_engine.retrieve_relevant_docs(query, limit=3)
        
        # Verify duplicates are removed
        doc_ids = [doc.KB_ID for doc in docs]
        self.assertEqual(len(doc_ids), len(set(doc_ids)), "Duplicates should be removed")
    
    def test_retrieve_relevant_docs_respects_limit(self):
        """Test that retrieve_relevant_docs respects the limit parameter"""
        # Create multiple mock documents
        mock_docs = []
        for i in range(10):
            mock_doc = Mock()
            mock_doc.KB_ID = i + 1
            mock_doc.Title = f"Document {i+1}"
            mock_docs.append(mock_doc)
        
        self.mock_kb_repo.search.return_value = mock_docs
        
        # Test with limit
        query = "test query"
        docs = self.rag_engine.retrieve_relevant_docs(query, limit=3)
        
        # Verify limit is respected
        self.assertLessEqual(len(docs), 3)
    
    def test_retrieve_relevant_docs_handles_empty_repository(self):
        """Test that retrieve_relevant_docs handles empty repository gracefully"""
        # Mock empty repository
        self.mock_kb_repo.search.return_value = []
        
        # Test retrieval
        query = "test query"
        docs = self.rag_engine.retrieve_relevant_docs(query, limit=3)
        
        # Verify empty list returned
        self.assertIsInstance(docs, list)
        self.assertEqual(len(docs), 0)
    
    def test_retrieve_user_context_retrieves_tasks(self):
        """Test that retrieve_user_context retrieves user tasks"""
        # Mock repositories
        mock_task = Mock()
        mock_task.Task_Title = "Complete Assignment"
        mock_task.Due_Date = date.today()
        mock_task.Priority = "High"
        mock_task.Status = "Pending"
        
        mock_task_repo = Mock()
        mock_task_repo.get_by_user_id.return_value = [mock_task]
        
        with patch('services.ai_assistant_service.RepositoryFactory') as mock_factory:
            mock_factory.get_repository.side_effect = lambda repo_type: {
                'task': mock_task_repo,
                'schedule': Mock(),
                'student': Mock(),
                'calendar': Mock()
            }.get(repo_type, Mock())
            
            rag_engine = RAGEngine()
            user_context = rag_engine.retrieve_user_context(user_id=1)
            
            # Verify tasks are retrieved
            self.assertIn('tasks', user_context)
            self.assertGreater(len(user_context['tasks']), 0)
            self.assertEqual(user_context['tasks'][0]['title'], "Complete Assignment")
    
    def test_retrieve_user_context_identifies_today_tasks(self):
        """Test that retrieve_user_context identifies tasks due today"""
        # Mock task due today
        mock_task = Mock()
        mock_task.Task_Title = "Today's Task"
        mock_task.Due_Date = datetime.now()  # Due today
        mock_task.Priority = "High"
        mock_task.Status = "Pending"
        
        mock_task_repo = Mock()
        mock_task_repo.get_by_user_id.return_value = [mock_task]
        
        with patch('services.ai_assistant_service.RepositoryFactory') as mock_factory:
            mock_factory.get_repository.side_effect = lambda repo_type: {
                'task': mock_task_repo,
                'schedule': Mock(),
                'student': Mock(),
                'calendar': Mock()
            }.get(repo_type, Mock())
            
            rag_engine = RAGEngine()
            user_context = rag_engine.retrieve_user_context(user_id=1)
            
            # Verify today's tasks are identified
            self.assertIn('today_tasks', user_context)
            self.assertGreater(len(user_context['today_tasks']), 0)
            self.assertEqual(user_context['today_tasks'][0]['title'], "Today's Task")
    
    def test_generate_answer_without_documents(self):
        """Test that generate_answer handles queries with no relevant documents"""
        # Test with empty documents
        result = self.rag_engine.generate_answer(
            query="test question",
            relevant_docs=[],
            user_context=None,
            llm_service=None
        )
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('answer', result)
        self.assertIn('sources', result)
        self.assertIn('confidence', result)
        self.assertIsInstance(result['sources'], list)
    
    def test_generate_answer_with_documents(self):
        """Test that generate_answer generates answer from documents"""
        # Create mock documents
        mock_doc = Mock()
        mock_doc.KB_ID = 1
        mock_doc.Title = "Test Document"
        mock_doc.Content = "This is test content about data structures."
        mock_doc.Category = "Courses"
        
        # Test answer generation
        result = self.rag_engine.generate_answer(
            query="What are data structures?",
            relevant_docs=[mock_doc],
            user_context=None,
            llm_service=None
        )
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('answer', result)
        self.assertIn('sources', result)
        self.assertIn('confidence', result)
        self.assertGreater(len(result['answer']), 0)
        self.assertEqual(len(result['sources']), 1)
    
    def test_get_rag_engine_returns_singleton(self):
        """Test that get_rag_engine returns a singleton instance"""
        # Get two instances
        engine1 = get_rag_engine()
        engine2 = get_rag_engine()
        
        # Verify they are the same instance
        self.assertIs(engine1, engine2, "get_rag_engine should return singleton")
    
    def test_extract_keywords_from_query(self):
        """Test that _extract_keywords extracts meaningful keywords"""
        query = "What are the prerequisites for Data Structures course?"
        keywords = self.rag_engine._extract_keywords(query)
        
        # Verify keywords are extracted
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        # Should extract meaningful words (not stop words)
        self.assertIn('prerequisites', keywords)
        self.assertIn('data', keywords)
        self.assertIn('structures', keywords)


if __name__ == '__main__':
    unittest.main()
