"""Tests for the GET /activities endpoint"""

import pytest


def test_get_activities_returns_200(client):
    """Test that GET /activities returns 200 status code"""
    response = client.get("/activities")
    assert response.status_code == 200


def test_get_activities_returns_all_activities(client, test_activities):
    """Test that GET /activities returns all activities"""
    response = client.get("/activities")
    data = response.json()
    
    assert len(data) == len(test_activities)
    for activity_name in test_activities:
        assert activity_name in data


def test_activity_has_required_fields(client):
    """Test that each activity has all required fields"""
    response = client.get("/activities")
    data = response.json()
    
    required_fields = {"description", "schedule", "max_participants", "participants"}
    
    for activity_name, activity in data.items():
        assert isinstance(activity, dict), f"{activity_name} should be a dict"
        assert required_fields.issubset(activity.keys()), \
            f"{activity_name} missing required fields: {required_fields - set(activity.keys())}"


def test_activity_fields_have_correct_types(client):
    """Test that activity fields have correct data types"""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity in data.items():
        assert isinstance(activity["description"], str), \
            f"{activity_name} description should be a string"
        assert isinstance(activity["schedule"], str), \
            f"{activity_name} schedule should be a string"
        assert isinstance(activity["max_participants"], int), \
            f"{activity_name} max_participants should be an integer"
        assert isinstance(activity["participants"], list), \
            f"{activity_name} participants should be a list"


def test_participants_are_strings(client):
    """Test that all participants are email strings"""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity in data.items():
        for participant in activity["participants"]:
            assert isinstance(participant, str), \
                f"{activity_name} participant should be a string, got {type(participant)}"
            assert "@" in participant, \
                f"{activity_name} participant '{participant}' is not a valid email format"


def test_activities_initial_state(client, test_activities):
    """Test that activities have the correct initial state"""
    response = client.get("/activities")
    data = response.json()
    
    # Verify initial participant counts for known activities
    assert "Chess Club" in data
    assert len(data["Chess Club"]["participants"]) == 2
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]
    
    assert "Tennis Club" in data
    assert len(data["Tennis Club"]["participants"]) == 0
    
    assert "Programming Class" in data
    assert len(data["Programming Class"]["participants"]) == 2


def test_activity_descriptions_not_empty(client):
    """Test that all activities have non-empty descriptions"""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity in data.items():
        assert activity["description"].strip(), \
            f"{activity_name} description should not be empty"


def test_activity_schedules_not_empty(client):
    """Test that all activities have non-empty schedules"""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity in data.items():
        assert activity["schedule"].strip(), \
            f"{activity_name} schedule should not be empty"


def test_max_participants_positive(client):
    """Test that max_participants is positive for all activities"""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity in data.items():
        assert activity["max_participants"] > 0, \
            f"{activity_name} max_participants should be positive, got {activity['max_participants']}"
