"""Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

import pytest


def test_unregister_success(client, test_activities):
    """Test successful unregister from an activity"""
    activity_name = "Chess Club"
    email = test_activities[activity_name]["participants"][0]
    initial_count = len(test_activities[activity_name]["participants"])
    
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    assert len(test_activities[activity_name]["participants"]) == initial_count - 1
    assert email not in test_activities[activity_name]["participants"]


def test_unregister_activity_not_found(client):
    """Test unregister when activity does not exist returns 404"""
    response = client.delete(
        "/activities/Nonexistent Activity/unregister",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_student_not_registered(client, test_activities):
    """Test unregister when student is not registered returns 400"""
    activity_name = "Tennis Club"  # Has no participants
    email = "notregistered@mergington.edu"
    
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "not registered" in data["detail"]


def test_unregister_removes_from_participants_list(client, test_activities):
    """Test that unregister properly removes student from participants list"""
    activity_name = "Programming Class"
    email = test_activities[activity_name]["participants"][0]
    
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 200
    assert email not in test_activities[activity_name]["participants"]


def test_unregister_response_message_format(client, test_activities):
    """Test that unregister response message has correct format"""
    activity_name = "Drama Club"
    email = test_activities[activity_name]["participants"][0]
    
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Unregistered {email}" in data["message"]
    assert activity_name in data["message"]


def test_unregister_decreases_participant_count(client, test_activities):
    """Test that unregister decreases participant count"""
    activity_name = "Science Club"
    initial_count = len(test_activities[activity_name]["participants"])
    email = test_activities[activity_name]["participants"][0]
    
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 200
    assert len(test_activities[activity_name]["participants"]) == initial_count - 1


def test_unregister_other_participants_unaffected(client, test_activities):
    """Test that other participants are unaffected by an unregister"""
    activity_name = "Basketball Team"
    unregister_email = test_activities[activity_name]["participants"][0]
    other_participants = test_activities[activity_name]["participants"][1:].copy()
    
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": unregister_email}
    )
    
    assert response.status_code == 200
    # Verify other participants are still there
    for participant in other_participants:
        assert participant in test_activities[activity_name]["participants"]


def test_unregister_cannot_unregister_twice(client, test_activities):
    """Test that same student cannot unregister twice"""
    activity_name = "Drama Club"
    email = test_activities[activity_name]["participants"][0]
    
    # First unregister should succeed
    response1 = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second unregister should fail
    response2 = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    assert response2.status_code == 400
    assert "not registered" in response2.json()["detail"]


def test_unregister_then_ressignup_allowed(client, test_activities):
    """Test that student can sign up again after unregistering"""
    activity_name = "Art Studio"
    email = "newstudent@mergington.edu"
    
    # Sign up
    response1 = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response1.status_code == 200
    assert email in test_activities[activity_name]["participants"]
    
    # Unregister
    response2 = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    assert response2.status_code == 200
    assert email not in test_activities[activity_name]["participants"]
    
    # Re-signup should work
    response3 = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response3.status_code == 200
    assert email in test_activities[activity_name]["participants"]


def test_unregister_case_sensitive_activity_name(client, test_activities):
    """Test that activity names are case sensitive"""
    # Add participant to test activity
    activity_name = "Debate Team"
    email = "debater@test.com"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Correct case - should succeed
    response1 = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Sign up again for next test
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Wrong case - should fail
    response2 = client.delete(
        f"/activities/debate team/unregister",
        params={"email": email}
    )
    assert response2.status_code == 404


def test_unregister_multiple_from_same_activity(client, test_activities):
    """Test unregistering multiple students from the same activity"""
    activity_name = "Gym Class"
    initial_count = len(test_activities[activity_name]["participants"])
    emails_to_remove = test_activities[activity_name]["participants"][:2]
    
    for email in emails_to_remove:
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify count decreased properly
    assert len(test_activities[activity_name]["participants"]) == initial_count - 2
    for email in emails_to_remove:
        assert email not in test_activities[activity_name]["participants"]
