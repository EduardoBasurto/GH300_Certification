"""Pytest configuration and shared fixtures"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path
import os
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from .fixtures import create_test_activities


@pytest.fixture
def test_activities():
    """Provide fresh test activities data for each test."""
    return create_test_activities()


@pytest.fixture
def app(test_activities):
    """Create a fresh FastAPI app instance with isolated test data."""
    app_instance = FastAPI(
        title="Mergington High School API",
        description="API for viewing and signing up for extracurricular activities"
    )
    
    # Mount static files
    current_dir = Path(__file__).parent.parent / "src"
    app_instance.mount(
        "/static",
        StaticFiles(directory=os.path.join(current_dir, "static")),
        name="static"
    )
    
    # Routes using test_activities
    @app_instance.get("/")
    def root():
        return RedirectResponse(url="/static/index.html")
    
    @app_instance.get("/activities")
    def get_activities():
        return test_activities
    
    @app_instance.post("/activities/{activity_name}/signup")
    def signup_for_activity(activity_name: str, email: str):
        """Sign up a student for an activity"""
        if activity_name not in test_activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        activity = test_activities[activity_name]
        
        if email in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student already signed up for this activity")
        
        activity["participants"].append(email)
        return {"message": f"Signed up {email} for {activity_name}"}
    
    @app_instance.delete("/activities/{activity_name}/unregister")
    def unregister_from_activity(activity_name: str, email: str):
        """Unregister a student from an activity"""
        if activity_name not in test_activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        activity = test_activities[activity_name]
        
        if email not in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student is not registered for this activity")
        
        activity["participants"].remove(email)
        return {"message": f"Unregistered {email} from {activity_name}"}
    
    return app_instance


@pytest.fixture
def client(app):
    """Provide a TestClient for the app."""
    return TestClient(app)
