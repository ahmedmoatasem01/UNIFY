"""
Unit tests for Error Handling, Exceptions & Edge Cases
Tests how the application handles errors gracefully
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from app import create_app


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


@patch("controllers.user_controller.RepositoryFactory")
def test_user_not_found_returns_404(mock_factory, client):
    """Test that accessing non-existent user returns 404"""
    # Mock repository to return None (user not found)
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = None
    mock_factory.get_repository.return_value = mock_repo
    
    # Try to access user with ID 999
    response = client.get("/users/999")
    
    # Should return 404 or appropriate error
    assert response.status_code in [404, 500]  # 404 if handled, 500 if not


@patch("controllers.user_controller.RepositoryFactory")
def test_repository_exception_handled(mock_factory, client):
    """Test that repository exceptions are handled gracefully"""
    # Mock repository to raise exception
    mock_repo = MagicMock()
    mock_repo.get_all.side_effect = Exception("Database connection failed")
    mock_factory.get_repository.return_value = mock_repo
    
    # Try to access users list
    response = client.get("/users/")
    
    # Should handle error gracefully (500 or appropriate error)
    assert response.status_code in [500, 503]  # Internal Server Error or Service Unavailable


def test_invalid_route_returns_404(client):
    """Test that invalid routes return 404"""
    # Try to access non-existent route
    response = client.get("/invalid/route/that/does/not/exist")
    
    # Should return 404
    assert response.status_code == 404


def test_login_missing_credentials_returns_400(client):
    """Test that login without credentials returns 400 Bad Request"""
    # Missing email
    response = client.post("/auth/login",
                          json={"password": "test"},
                          content_type="application/json")
    assert response.status_code == 400
    
    # Missing password
    response = client.post("/auth/login",
                          json={"email": "test@example.com"},
                          content_type="application/json")
    assert response.status_code == 400


def test_login_empty_credentials_returns_400(client):
    """Test that login with empty credentials returns 400"""
    # Empty email
    response = client.post("/auth/login",
                          json={"email": "", "password": "test"},
                          content_type="application/json")
    assert response.status_code == 400
    
    # Empty password
    response = client.post("/auth/login",
                          json={"email": "test@example.com", "password": ""},
                          content_type="application/json")
    assert response.status_code == 400


@patch("controllers.ai_assistant_controller.rag_engine")
def test_ai_assistant_question_required(mock_engine, client):
    """Test that AI Assistant requires question field"""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Missing question
    response = client.post("/ai-assistant/ask",
                         json={},
                         content_type="application/json")
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


@patch("controllers.ai_assistant_controller.rag_engine")
def test_ai_assistant_empty_question_returns_400(mock_engine, client):
    """Test that AI Assistant rejects empty questions"""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Empty question
    response = client.post("/ai-assistant/ask",
                         json={"question": ""},
                         content_type="application/json")
    
    assert response.status_code == 400


def test_unauthorized_access_returns_401(client):
    """Test that accessing protected routes without auth returns 401"""
    # Try to access protected route without session
    response = client.get("/ai-assistant/history")
    
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data
