"""
Pytest configuration and fixtures
Provides Flask test client fixture for all tests
"""
import pytest
import sys
import os

# Add src directory to path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, src_path)

# Import Flask app
from app import create_app


@pytest.fixture
def app():
    """Create Flask application instance for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    return app


@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()


@pytest.fixture
def authenticated_client(client):
    """Create authenticated test client with session"""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'
    return client
