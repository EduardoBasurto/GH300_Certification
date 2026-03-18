"""Pytest configuration and shared fixtures"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
from copy import deepcopy

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app as production_app
from .fixtures import create_test_activities


@pytest.fixture
def test_activities():
    """Provide fresh test activities data for each test."""
    return create_test_activities()


@pytest.fixture
def app_with_test_data(test_activities):
    """Create an app instance with test data by monkey-patching the activities dict."""
    # Create a reference to the production app
    test_app = production_app
    
    # We need to replace the activities dict in the app's module
    # Import the app module to access its activities variable
    import app as app_module
    
    # Save original activities
    original_activities = app_module.activities.copy()
    
    # Replace with test activities
    app_module.activities.clear()
    app_module.activities.update(test_activities)
    
    yield test_app
    
    # Restore original activities after test
    app_module.activities.clear()
    app_module.activities.update(original_activities)


@pytest.fixture
def client(app_with_test_data):
    """Provide a TestClient for the app."""
    return TestClient(app_with_test_data)
