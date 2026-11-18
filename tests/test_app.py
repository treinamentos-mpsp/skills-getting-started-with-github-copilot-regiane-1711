from urllib.parse import quote

from src.app import activities


def test_get_activities_returns_activity_details(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activity = response.json()[activity_name]
    assert activity["description"]
    assert activity["schedule"]
    assert activity["max_participants"] > 0
    assert isinstance(activity["participants"], list)


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Basketball Club"
    email = "student@example.com"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name, safe='')}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Basketball Club"
    email = "student@example.com"
    activities[activity_name]["participants"].append(email)

    # Act
    response = client.post(
        f"/activities/{quote(activity_name, safe='')}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"].count(email) == 1


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@example.com"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name, safe='')}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_cancel_signup_removes_participant(client):
    # Arrange
    activity_name = "Basketball Club"
    email = "student+club@example.com"
    activities[activity_name]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name, safe='')}/participants/{quote(email, safe='')}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Canceled signup for {email} in {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_cancel_signup_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@example.com"

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name, safe='')}/participants/{quote(email, safe='')}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_cancel_signup_returns_404_for_unregistered_participant(client):
    # Arrange
    activity_name = "Basketball Club"
    email = "not-signed-up@example.com"

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name, safe='')}/participants/{quote(email, safe='')}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"