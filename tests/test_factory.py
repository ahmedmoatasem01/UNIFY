"""
Unit tests for Factory Pattern
Tests that RepositoryFactory returns correct repository instances
"""
import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from repositories.repository_factory import RepositoryFactory


def test_factory_returns_user_repo():
    """Test that factory returns UserRepository for 'user' type"""
    repo = RepositoryFactory.get_repository("user")
    from repositories.user.repository import UserRepository
    assert isinstance(repo, UserRepository)


def test_factory_returns_knowledge_base_repo():
    """Test that factory returns KnowledgeBaseRepository for 'knowledge_base' type"""
    repo = RepositoryFactory.get_repository("knowledge_base")
    from repositories.knowledge_base.repository import KnowledgeBaseRepository
    assert isinstance(repo, KnowledgeBaseRepository)


def test_factory_returns_chat_history_repo():
    """Test that factory returns ChatHistoryRepository for 'chat_history' type"""
    repo = RepositoryFactory.get_repository("chat_history")
    from repositories.chat_history.repository import ChatHistoryRepository
    assert isinstance(repo, ChatHistoryRepository)


def test_factory_case_insensitive():
    """Test that factory handles case-insensitive entity types"""
    repo1 = RepositoryFactory.get_repository("USER")
    repo2 = RepositoryFactory.get_repository("user")
    repo3 = RepositoryFactory.get_repository("User")
    
    from repositories.user.repository import UserRepository
    assert isinstance(repo1, UserRepository)
    assert isinstance(repo2, UserRepository)
    assert isinstance(repo3, UserRepository)


def test_factory_invalid_type():
    """Test that factory raises ValueError for unknown repository type"""
    with pytest.raises(ValueError) as exc_info:
        RepositoryFactory.get_repository("unknown_type")
    assert "Unknown repository type" in str(exc_info.value)


def test_factory_returns_different_instances():
    """Test that factory returns new instances (not singleton)"""
    repo1 = RepositoryFactory.get_repository("user")
    repo2 = RepositoryFactory.get_repository("user")
    
    # Should be different instances
    assert repo1 is not repo2


def test_factory_alternative_names():
    """Test that factory handles alternative names (e.g., 'kb' for 'knowledge_base')"""
    repo1 = RepositoryFactory.get_repository("knowledge_base")
    repo2 = RepositoryFactory.get_repository("kb")
    
    from repositories.knowledge_base.repository import KnowledgeBaseRepository
    assert isinstance(repo1, KnowledgeBaseRepository)
    assert isinstance(repo2, KnowledgeBaseRepository)
