"""Tests for the POST /activities/{activity_name}/signup endpoint"""

import pytest


def test_signup_success(client, test_activities):
    """Test successful signup for an activity"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    initial_count = len(test_activities[activity_name]["participants"])
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    assert len(test_activities[activity_name]["participants"]) == initial_count + 1
    assert email in test_activities[activity_name]["participants"]


def test_signup_activity_not_found(client):
    """Test signup when activity does not exist returns 404"""
    # Arrange
    nonexistent_activity = "Nonexistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{nonexistent_activity}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_already_registered(client, test_activities):
    """Test signup when student is already registered returns 400"""
    # Arrange
    activity_name = "Chess Club"
    email = test_activities[activity_name]["participants"][0]  # Use existing participant
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" in data["detail"]


def test_signup_multiple_students_same_activity(client, test_activities):
    """Test that multiple different students can sign up for the same activity"""
    # Arrange
    activity_name = "Tennis Club"  # Use activity with no participants
    email1 = "student1@mergington.edu"
    email2 = "student2@mergington.edu"
    
    # Act
    response1 = client.post(f"/activities/{activity_name}/signup", params={"email": email1})
    response2 = client.post(f"/activities/{activity_name}/signup", params={"email": email2})
    
    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert email1 in test_activities[activity_name]["participants"]
    assert email2 in test_activities[activity_name]["participants"]
    assert len(test_activities[activity_name]["participants"]) == 2


def test_signup_cannot_signup_duplicate(client, test_activities):
    """Test that same student cannot sign up twice"""
    # Arrange
    activity_name = "Tennis Club"
    email = "student@mergington.edu"
    
    # Act - First signup
    response1 = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    # Act - Second signup with same email
    response2 = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_adds_to_participants_list(client, test_activities):
    """Test that signup properly adds student to participants list"""
    # Arrange
    activity_name = "Art Studio"
    email = "artist@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    assert email in test_activities[activity_name]["participants"]


def test_signup_response_message_format(client):
    """Test that signup response message has correct format"""
    # Arrange
    email = "test@mergington.edu"
    activity_name = "Debate Team"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email}" in data["message"]
    assert activity_name in data["message"]


def test_signup_empty_activity_no_effect(client, test_activities):
    """Test signup updates count for empty activities"""
    # Arrange
    activity_name = "Tennis Club"
    initial_count = len(test_activities[activity_name]["participants"])
    email = "first@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    assert len(test_activities[activity_name]["participants"]) == initial_count + 1


def test_signup_existing_participants_unaffected(client, test_activities):
    """Test that existing participants are unaffected by new signup"""
    # Arrange
    activity_name = "Programming Class"
    original_participants = test_activities[activity_name]["participants"].copy()
    new_email = "newie@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})
    
    # Assert
    assert response.status_code == 200
    for participant in original_participants:
        assert participant in test_activities[activity_name]["participants"]


def test_signup_case_sensitive_activity_name(client):
    """Test that activity names are case sensitive"""
    # Arrange
    valid_activity = "Chess Club"
    invalid_activity = "chess club"
    email1 = "test@mergington.edu"
    email2 = "test2@mergington.edu"
    
    # Act
    response_valid = client.post(
        f"/activities/{valid_activity}/signup",
        params={"email": email1}
    )
    response_invalid = client.post(
        f"/activities/{invalid_activity}/signup",
        params={"email": email2}
    )
    
    # Assert
    assert response_valid.status_code == 200
    assert response_invalid.status_code == 404


def test_signup_allows_overflow_past_max_capacity(client, test_activities):
    """Test that signup allows exceeding max_participants (no capacity enforcement)"""
    # Arrange
    activity_name = "Tennis Club"
    test_activities[activity_name]["max_participants"] = 2
    emails = ["student1@test.com", "student2@test.com", "student3@test.com"]
    
    # Act
    responses = []
    for email in emails:
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        responses.append(response)
    
    # Assert
    for response in responses:
        assert response.status_code == 200
    assert len(test_activities[activity_name]["participants"]) == 3
    for email in emails:
        assert email in test_activities[activity_name]["participants"]
