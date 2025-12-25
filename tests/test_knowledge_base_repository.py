"""
Unit tests for Knowledge Base Repository
Tests data access layer for knowledge base operations
"""
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from src.repositories.knowledge_base.repository import KnowledgeBaseRepository
from src.models.knowledge_base import KnowledgeBase


class TestKnowledgeBaseRepository(unittest.TestCase):
    """Test cases for Knowledge Base Repository"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock database connection
        self.mock_conn = Mock()
        self.mock_cursor = Mock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        
        # Create repository with mocked connection
        with patch('repositories.knowledge_base.repository.DatabaseConnection') as mock_db:
            mock_db.get_instance.return_value.get_connection.return_value = self.mock_conn
            self.repo = KnowledgeBaseRepository()
    
    def test_search_by_keyword(self):
        """Test that search method finds documents by keyword"""
        # Mock database results
        mock_result = [
            (1, "Data Structures", "Content about data structures", "Courses", "data,structures", None, None, None)
        ]
        self.mock_cursor.fetchall.return_value = mock_result
        
        # Test search
        results = self.repo.search("data structures", limit=5)
        
        # Verify
        self.assertIsInstance(results, list)
        self.mock_cursor.execute.assert_called()
        # Verify SQL contains search terms
        execute_call = str(self.mock_cursor.execute.call_args)
        self.assertIn('data', execute_call.lower() or 'structures' in execute_call.lower())
    
    def test_get_by_id(self):
        """Test that get_by_id retrieves a specific document"""
        # Mock database result
        mock_result = (1, "Test Document", "Content", "Category", "keywords", None, None, None)
        self.mock_cursor.fetchone.return_value = mock_result
        
        # Test get by ID
        doc = self.repo.get_by_id(1)
        
        # Verify
        self.assertIsNotNone(doc)
        self.assertEqual(doc.KB_ID, 1)
        self.mock_cursor.execute.assert_called()
    
    def test_get_categories(self):
        """Test that get_categories returns all unique categories"""
        # Mock database results
        mock_results = [
            ("Courses",),
            ("Policies",),
            ("Resources",)
        ]
        self.mock_cursor.fetchall.return_value = mock_results
        
        # Test get categories
        categories = self.repo.get_categories()
        
        # Verify
        self.assertIsInstance(categories, list)
        self.assertGreater(len(categories), 0)
        self.assertIn("Courses", categories)
    
    def test_search_by_category(self):
        """Test that search_by_category filters documents by category"""
        # Mock database results
        mock_results = [
            (1, "Course 1", "Content", "Courses", None, None, None, None),
            (2, "Course 2", "Content", "Courses", None, None, None, None)
        ]
        self.mock_cursor.fetchall.return_value = mock_results
        
        # Test search by category
        results = self.repo.search_by_category("Courses")
        
        # Verify
        self.assertIsInstance(results, list)
        self.mock_cursor.execute.assert_called()
        # All results should be from Courses category
        for doc in results:
            self.assertEqual(doc.Category, "Courses")
    
    def test_add_document(self):
        """Test that add method inserts a new document"""
        # Create test document
        doc = KnowledgeBase(
            Title="Test Document",
            Content="Test content",
            Category="Test",
            Keywords="test,keywords"
        )
        
        # Mock cursor for insert
        self.mock_cursor.lastrowid = 1
        
        # Test add
        result = self.repo.add(doc)
        
        # Verify
        self.mock_cursor.execute.assert_called()
        self.mock_conn.commit.assert_called()
    
    def test_update_document(self):
        """Test that update method modifies an existing document"""
        # Create test document with ID
        doc = KnowledgeBase(
            KB_ID=1,
            Title="Updated Title",
            Content="Updated content",
            Category="Updated",
            Keywords="updated,keywords"
        )
        
        # Test update
        result = self.repo.update(doc)
        
        # Verify
        self.mock_cursor.execute.assert_called()
        self.mock_conn.commit.assert_called()


if __name__ == '__main__':
    unittest.main()
