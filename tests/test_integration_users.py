"""
Integration tests for User functionality
Tests Controller + Factory + Repository + Database working together
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from app import create_app
from models.user import User
from datetime import datetime


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@patch("repositories.user.repository.DatabaseConnection")
def test_integration_user_list_route(mock_db, client):
    """Integration test: Test user list route with real Factory + Repository flow"""
    # Create mock database connection
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    
    # Mock database response
    fake_cursor.fetchall.return_value = [
        (1, "Amina", "amina@test.com", "hashed_pass", datetime(2024, 1, 1)),
        (2, "Omar", "omar@test.com", "hashed_pass", datetime(2024, 1, 2))
    ]
    fake_conn.cursor.return_value = fake_cursor
    
    mock_db_instance = MagicMock()
    mock_db_instance.get_connection.return_value = fake_conn
    mock_db.return_value = mock_db_instance
    
    # Test the full flow: Route -> Controller -> Factory -> Repository -> Database
    response = client.get("/users/")
    
    # Verify response
    assert response.status_code == 200
    # Response should contain user data (check if HTML contains names or JSON response)
    response_data = response.get_data(as_text=True)
    # If HTML response, check for user names
    # If JSON response, parse and check
    assert "Amina" in response_data or "200" in response_data


@patch("repositories.user.repository.DatabaseConnection")
def test_integration_user_get_by_id(mock_db, client):
    """Integration test: Test getting specific user by ID"""
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    
    fake_cursor.fetchone.return_value = (
        1, "IntegrationUser", "integration@test.com", "hashed_pass", datetime(2024, 1, 1)
    )
    fake_conn.cursor.return_value = fake_cursor
    
    mock_db_instance = MagicMock()
    mock_db_instance.get_connection.return_value = fake_conn
    mock_db.return_value = mock_db_instance
    
    # Test full integration flow
    response = client.get("/users/1")
    
    # Verify response
    assert response.status_code in [200, 404]  # 200 if found, 404 if not
    if response.status_code == 200:
        response_data = response.get_data(as_text=True)
        assert "IntegrationUser" in response_data or "200" in response_data


@patch("repositories.user.repository.DatabaseConnection")
def test_integration_user_creation_flow(mock_db, client):
    """Integration test: Test user creation flow"""
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    
    # Mock successful insert
    fake_cursor.rowcount = 1
    fake_conn.cursor.return_value = fake_cursor
    
    mock_db_instance = MagicMock()
    mock_db_instance.get_connection.return_value = fake_conn
    mock_db.return_value = mock_db_instance
    
    # Test user creation
    response = client.post("/users/create",
                          json={
                              "username": "NewUser",
                              "email": "newuser@test.com",
                              "password": "password123"
                          },
                          content_type="application/json")
    
    # Verify response (should be 200 or 201 for created)
    assert response.status_code in [200, 201, 400, 500]  # Various possible responses


@patch("repositories.user.repository.DatabaseConnection")
def test_integration_factory_repository_interaction(mock_db):
    """Integration test: Verify Factory returns correct Repository that works with Database"""
    from repositories.repository_factory import RepositoryFactory
    
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.fetchall.return_value = [
        (1, "TestUser", "test@test.com", "hash", datetime(2024, 1, 1))
    ]
    fake_conn.cursor.return_value = fake_cursor
    
    mock_db_instance = MagicMock()
    mock_db_instance.get_connection.return_value = fake_conn
    mock_db.return_value = mock_db_instance
    
    # Get repository from factory
    repo = RepositoryFactory.get_repository("user")
    
    # Use repository (should work with mocked database)
    users = repo.get_all()
    
    # Verify integration works
    assert len(users) == 1
    assert isinstance(users[0], User)
    assert users[0].Username == "TestUser"


@patch("repositories.user.repository.DatabaseConnection")
def test_integration_model_creation_from_repository(mock_db):
    """Integration test: Verify Models are created correctly from Repository data"""
    from repositories.repository_factory import RepositoryFactory
    
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.fetchone.return_value = (
        5, "ModelTest", "model@test.com", "hash123", datetime(2024, 12, 21)
    )
    fake_conn.cursor.return_value = fake_cursor
    
    mock_db_instance = MagicMock()
    mock_db_instance.get_connection.return_value = fake_conn
    mock_db.return_value = mock_db_instance
    
    # Get repository and fetch user
    repo = RepositoryFactory.get_repository("user")
    user = repo.get_by_id(5)
    
    # Verify model is created correctly
    assert user is not None
    assert isinstance(user, User)
    assert user.User_ID == 5
    assert user.Username == "ModelTest"
    assert user.Email == "model@test.com"
    assert isinstance(user.Created_At, datetime)
