"""
Unit tests for Singleton Pattern
Tests that DatabaseConnection returns the same instance
"""
import pytest
import sys
import os
from unittest.mock import patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from core.db_singleton import DatabaseConnection


def test_singleton_instance():
    """Test that DatabaseConnection returns the same instance"""
    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    
    # Should be the same instance (singleton)
    assert db1 is db2


def test_singleton_get_instance():
    """Test that get_instance() returns the same singleton instance"""
    db1 = DatabaseConnection.get_instance()
    db2 = DatabaseConnection.get_instance()
    db3 = DatabaseConnection()
    
    # All should be the same instance
    assert db1 is db2
    assert db1 is db3
    assert db2 is db3


def test_singleton_preserves_state():
    """Test that singleton preserves state across calls"""
    db1 = DatabaseConnection()
    db1.test_attribute = "test_value"
    
    db2 = DatabaseConnection()
    
    # Should have the same attribute
    assert hasattr(db2, 'test_attribute')
    assert db2.test_attribute == "test_value"


def test_singleton_initialized_once():
    """Test that singleton initialization happens only once"""
    db1 = DatabaseConnection()
    initial_connection_string = db1.connection_string
    
    db2 = DatabaseConnection()
    
    # Should have same connection string (initialized once)
    assert db2.connection_string == initial_connection_string
