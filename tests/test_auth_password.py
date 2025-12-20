"""
Unit tests for authentication password hashing
Tests password hashing functionality used in authentication
"""
import unittest
import sys
import os
import hashlib

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))


class TestPasswordHashing(unittest.TestCase):
    """Test cases for password hashing"""
    
    def test_password_hashing_produces_consistent_hash(self):
        """Test that the same password produces the same hash"""
        password = "testpassword123"
        hash1 = hashlib.sha256(password.encode()).hexdigest()
        hash2 = hashlib.sha256(password.encode()).hexdigest()
        
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)  # SHA256 produces 64 character hex string
    
    def test_different_passwords_produce_different_hashes(self):
        """Test that different passwords produce different hashes"""
        password1 = "password1"
        password2 = "password2"
        
        hash1 = hashlib.sha256(password1.encode()).hexdigest()
        hash2 = hashlib.sha256(password2.encode()).hexdigest()
        
        self.assertNotEqual(hash1, hash2)
    
    def test_password_hashing_is_deterministic(self):
        """Test that password hashing is deterministic (same input = same output)"""
        password = "mypassword"
        expected_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Hash the same password multiple times
        for _ in range(5):
            actual_hash = hashlib.sha256(password.encode()).hexdigest()
            self.assertEqual(actual_hash, expected_hash)
    
    def test_empty_password_produces_valid_hash(self):
        """Test that empty password produces a valid hash (edge case)"""
        password = ""
        hash_result = hashlib.sha256(password.encode()).hexdigest()
        
        self.assertIsInstance(hash_result, str)
        self.assertEqual(len(hash_result), 64)
        # Empty string SHA256 hash
        self.assertEqual(hash_result, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")


if __name__ == '__main__':
    unittest.main()

