"""
Unit tests for User model
Tests the User model's core functionality including initialization and serialization
"""
import unittest
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from src.models.user import User


class TestUserModel(unittest.TestCase):
    """Test cases for User model"""
    
    def test_user_initialization_with_all_fields(self):
        """Test User can be initialized with all fields"""
        user = User(
            User_ID=1,
            Username="testuser",
            Email="test@example.com",
            Password_Hash="hashed_password"
        )
        self.assertEqual(user.User_ID, 1)
        self.assertEqual(user.Username, "testuser")
        self.assertEqual(user.Email, "test@example.com")
        self.assertEqual(user.Password_Hash, "hashed_password")
        self.assertIsInstance(user.Created_At, datetime)
    
    def test_user_initialization_minimal(self):
        """Test User can be initialized with minimal fields"""
        user = User()
        self.assertIsNone(user.User_ID)
        self.assertEqual(user.Username, "")
        self.assertEqual(user.Email, "")
        self.assertEqual(user.Password_Hash, "")
        self.assertIsInstance(user.Created_At, datetime)
    
    def test_user_to_dict(self):
        """Test User.to_dict() returns correct dictionary representation"""
        created_at = datetime(2024, 1, 1, 12, 0, 0)
        user = User(
            User_ID=1,
            Username="testuser",
            Email="test@example.com",
            Password_Hash="hashed_password",
            Created_At=created_at
        )
        user_dict = user.to_dict()
        
        self.assertEqual(user_dict['User_ID'], 1)
        self.assertEqual(user_dict['Username'], "testuser")
        self.assertEqual(user_dict['Email'], "test@example.com")
        self.assertEqual(user_dict['Password_Hash'], "hashed_password")
        self.assertEqual(user_dict['Created_At'], created_at)
        self.assertEqual(len(user_dict), 5)


if __name__ == '__main__':
    unittest.main()

