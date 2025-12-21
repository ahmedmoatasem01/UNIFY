"""
Unit tests for Repositories (With Mocks)
Tests repository data access layer with mocked database calls
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch, Mock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from repositories.user.repository import UserRepository
from models.user import User
from datetime import datetime


@patch("repositories.user.repository.DatabaseConnection")
def test_get_all_users(mock_db):
    """Test that UserRepository.get_all() returns list of users"""
    # Create mock database connection
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    
    # Mock fetchall to return user data
    fake_cursor.fetchall.return_value = [
        (1, "Ali", "ali@example.com", "hashed_password", datetime(2024, 1, 1))
    ]
    fake_conn.cursor.return_value = fake_cursor
    
    # Configure mock database
    mock_db_instance = MagicMock()
    mock_db_instance.get_connection.return_value = fake_conn
    mock_db.return_value = mock_db_instance
    
    # Test repository
    repo = UserRepository()
    users = repo.get_all()
    
    # Verify results
    assert len(users) == 1
    assert isinstance(users[0], User)
    assert users[0].User_ID == 1
    assert users[0].Username == "Ali"
    assert users[0].Email == "ali@example.com"
    
    # Verify database was called
    fake_cursor.execute.assert_called_once()
    fake_cursor.close.assert_called_once()
    fake_conn.close.assert_called_once()


@patch("repositories.user.repository.DatabaseConnection")
def test_get_by_id_user_found(mock_db):
    """Test that UserRepository.get_by_id() returns user when found"""
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    
    # Mock fetchone to return user data
    fake_cursor.fetchone.return_value = (
        1, "Sara", "sara@example.com", "hashed_password", datetime(2024, 1, 1)
    )
    fake_conn.cursor.return_value = fake_cursor
    
    mock_db_instance = MagicMock()
    mock_db_instance.get_connection.return_value = fake_conn
    mock_db.return_value = mock_db_instance
    
    # Test repository
    repo = UserRepository()
    user = repo.get_by_id(1)
    
    # Verify results
    assert user is not None
    assert isinstance(user, User)
    assert user.User_ID == 1
    assert user.Username == "Sara"
    assert user.Email == "sara@example.com"


@patch("repositories.user.repository.DatabaseConnection")
def test_get_by_id_user_not_found(mock_db):
    """Test that UserRepository.get_by_id() returns None when user not found"""
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    
    # Mock fetchone to return None (user not found)
    fake_cursor.fetchone.return_value = None
    fake_conn.cursor.return_value = fake_cursor
    
    mock_db_instance = MagicMock()
    mock_db_instance.get_connection.return_value = fake_conn
    mock_db.return_value = mock_db_instance
    
    # Test repository
    repo = UserRepository()
    user = repo.get_by_id(999)
    
    # Verify results
    assert user is None


@patch("repositories.user.repository.DatabaseConnection")
def test_get_by_email_user_found(mock_db):
    """Test that UserRepository.get_by_email() returns user when found"""
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    
    fake_cursor.fetchone.return_value = (
        1, "TestUser", "test@example.com", "hashed_password", datetime(2024, 1, 1)
    )
    fake_conn.cursor.return_value = fake_cursor
    
    mock_db_instance = MagicMock()
    mock_db_instance.get_connection.return_value = fake_conn
    mock_db.return_value = mock_db_instance
    
    repo = UserRepository()
    user = repo.get_by_email("test@example.com")
    
    assert user is not None
    assert isinstance(user, User)
    assert user.Email == "test@example.com"


@patch("repositories.user.repository.DatabaseConnection")
def test_get_all_users_empty_result(mock_db):
    """Test that UserRepository.get_all() handles empty result set"""
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    
    # Mock empty result
    fake_cursor.fetchall.return_value = []
    fake_conn.cursor.return_value = fake_cursor
    
    mock_db_instance = MagicMock()
    mock_db_instance.get_connection.return_value = fake_conn
    mock_db.return_value = mock_db_instance
    
    repo = UserRepository()
    users = repo.get_all()
    
    assert isinstance(users, list)
    assert len(users) == 0
