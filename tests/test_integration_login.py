"""
Integration test for login route
Tests the login endpoint end-to-end including request/response flow
"""
import unittest
import sys
import os
from flask import Flask
from unittest.mock import patch, MagicMock

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_path)

# Import app from src
from app import app
import json


class TestLoginIntegration(unittest.TestCase):
    """Integration tests for login route"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = self.app.test_client()
    
    def test_login_route_exists(self):
        """Test that login route exists and accepts POST requests"""
        response = self.client.post('/auth/login',
                                  data=json.dumps({'email': 'test@example.com', 'password': 'test'}),
                                  content_type='application/json')
        # Should not return 404 (route exists)
        # May return 401/500 if DB unavailable, but not 404
        self.assertNotEqual(response.status_code, 404)
        self.assertEqual(response.content_type, 'application/json')
    
    def test_login_with_missing_credentials_returns_400(self):
        """Test that login without email or password returns 400 Bad Request"""
        # Missing email
        response = self.client.post('/auth/login',
                                  data=json.dumps({'password': 'test'}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('required', data['error'].lower())
        
        # Missing password
        response = self.client.post('/auth/login',
                                  data=json.dumps({'email': 'test@example.com'}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('required', data['error'].lower())
    
    def test_login_with_empty_credentials_returns_400(self):
        """Test that login with empty email or password returns 400 Bad Request"""
        # Empty email
        response = self.client.post('/auth/login',
                                  data=json.dumps({'email': '', 'password': 'test'}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
        # Empty password
        response = self.client.post('/auth/login',
                                  data=json.dumps({'email': 'test@example.com', 'password': ''}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_login_response_format(self):
        """Test that login response has correct JSON format"""
        response = self.client.post('/auth/login',
                                  data=json.dumps({
                                      'email': 'test@example.com',
                                      'password': 'testpassword'
                                  }),
                                  content_type='application/json')
        
        # Should be valid JSON
        self.assertEqual(response.content_type, 'application/json')
        try:
            data = json.loads(response.data)
            # Response should either be success (with message and user) or error
            # Status code may vary based on DB availability, but format should be consistent
            if response.status_code == 200:
                self.assertIn('message', data)
                self.assertIn('user', data)
            else:
                # For errors (400, 401, 500), should have error field
                self.assertIn('error', data)
        except json.JSONDecodeError:
            self.fail("Response is not valid JSON")


if __name__ == '__main__':
    unittest.main()

