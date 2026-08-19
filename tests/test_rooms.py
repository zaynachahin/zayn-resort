from fastapi import status
import pytest

# ==================== DADOS / FIXTURES ====================

fake_room_id = "00000000-0000-0000-0000-000000000001"
fake_category_id = "00000000-0000-0000-0000-000000000002"

fake_room = [
    (
        "00000000-0000-0000-0000-000000000001",
        "101",
        "Test Room",
        "Test Description",
        "00000000-0000-0000-0000-000000000002",
    )
]

fake_room_category = [
    (
        "00000000-0000-0000-0000-000000000002",
        "Test Category",
        2,
        200,
    )
]

expected_room = {
    "room_id": "00000000-0000-0000-0000-000000000001",
    "number": "101",
    "name": "Test Room",
    "description": "Test Description",
    "room_category_id": "00000000-0000-0000-0000-000000000002",
}

@pytest.fixture
def valid_room_payload():
    return {
        "number": "101",
        "name": "Test Room",
        "description": "Test Description",
        "room_category_id": fake_category_id,
    }


# ==================== GET LIST ====================

def test_list_rooms_returns_200(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.list_rooms",
        lambda: fake_room,
    )

    # Act
    response = client.get("/rooms")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [expected_room]


def test_list_rooms_returns_empty_list(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.list_rooms",
        lambda: [],
    )

    # Act
    response = client.get("/rooms")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


# ==================== GET BY ID ====================

def test_get_room_returns_200(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_id",
        lambda id: fake_room,
    )

    # Act
    response = client.get(f"/rooms/{fake_room_id}")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_room


def test_get_room_returns_404_when_not_exists(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_id",
        lambda id: [],
    )

    # Act
    response = client.get(f"/rooms/{fake_room_id}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room not found"


def test_get_room_returns_422_when_id_invalid(client):
    # Act
    response = client.get("/rooms/abc")

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# ==================== CREATE ====================

def test_create_room_with_valid_payload_returns_201(monkeypatch, client, valid_room_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.get_room_category_by_id",
        lambda id: fake_room_category,
    )
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_number",
        lambda number: [],
    )
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.create_room",
        lambda number, name, description, room_category_id: fake_room_id,
    )

    # Act
    response = client.post("/rooms", json=valid_room_payload)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["room_id"] == fake_room_id


def test_create_room_with_invalid_category_returns_404(monkeypatch, client, valid_room_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.get_room_category_by_id",
        lambda id: [],
    )

    # Act
    response = client.post("/rooms", json=valid_room_payload)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room category not found"


def test_create_room_with_duplicate_number_returns_409(monkeypatch, client, valid_room_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.get_room_category_by_id",
        lambda id: fake_room_category,
    )
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_number",
        lambda number: fake_room,
    )

    # Act
    response = client.post("/rooms", json=valid_room_payload)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Room number already exists"


@pytest.mark.parametrize("missing_field", ["number", "name", "room_category_id"])
def test_create_room_with_missing_field_returns_422(missing_field, client, valid_room_payload):
    # Arrange
    payload = valid_room_payload.copy()
    del payload[missing_field]

    # Act
    response = client.post("/rooms", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# ==================== PUT ====================

def test_update_room_with_valid_payload_returns_200(monkeypatch, client, valid_room_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_id",
        lambda id: fake_room,
    )
    monkeypatch.setattr(
        "app.routes.room_routes.get_room_category_by_id",
        lambda id: fake_room_category,
    )
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_number_excluding_id",
        lambda number, id: [],
    )
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.update_room",
        lambda id, number, name, description, room_category_id: fake_room,
    )

    # Act
    response = client.put(f"/rooms/{fake_room_id}", json=valid_room_payload)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Room updated successfully"


def test_update_room_returns_404_when_not_exists(monkeypatch, client, valid_room_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_id",
        lambda id: [],
    )

    # Act
    response = client.put(f"/rooms/{fake_room_id}", json=valid_room_payload)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room not found"


def test_update_room_returns_404_when_category_not_exists(monkeypatch, client, valid_room_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_id",
        lambda id: fake_room,
    )
    monkeypatch.setattr(
        "app.routes.room_routes.get_room_category_by_id",
        lambda id: [],
    )

    # Act
    response = client.put(f"/rooms/{fake_room_id}", json=valid_room_payload)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room category not found"


def test_update_room_returns_409_when_number_belongs_to_another(monkeypatch, client, valid_room_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_id",
        lambda id: fake_room,
    )
    monkeypatch.setattr(
        "app.routes.room_routes.get_room_category_by_id",
        lambda id: fake_room_category,
    )
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_number_excluding_id",
        lambda number, id: fake_room,
    )

    # Act
    response = client.put(f"/rooms/{fake_room_id}", json=valid_room_payload)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Room number already exists"


# ==================== PATCH ====================

def test_patch_room_with_valid_payload_returns_200(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_id",
        lambda id: fake_room,
    )
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.patch_room",
        lambda id, fields: fake_room,
    )

    # Act
    response = client.patch(f"/rooms/{fake_room_id}", json={"name": "New Name"})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Room updated successfully"


def test_patch_room_returns_404_when_not_exists(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_id",
        lambda id: [],
    )

    # Act
    response = client.patch(f"/rooms/{fake_room_id}", json={"name": "New Name"})

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room not found"


def test_patch_room_returns_400_when_body_empty(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_id",
        lambda id: fake_room,
    )

    # Act
    response = client.patch(f"/rooms/{fake_room_id}", json={})

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "No fields provided"


def test_patch_room_returns_404_when_category_not_exists(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_id",
        lambda id: fake_room,
    )
    monkeypatch.setattr(
        "app.routes.room_routes.get_room_category_by_id",
        lambda id: [],
    )

    # Act
    response = client.patch(f"/rooms/{fake_room_id}", json={"room_category_id": fake_category_id})

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room category not found"


def test_patch_room_returns_409_when_number_belongs_to_another(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_id",
        lambda id: fake_room,
    )
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_number_excluding_id",
        lambda number, id: fake_room,
    )

    # Act
    response = client.patch(f"/rooms/{fake_room_id}", json={"number": "101"})

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Room number already exists"


# ==================== DELETE ====================

def test_delete_room_returns_204(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_id_including_deleted",
        lambda id: fake_room,
    )
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.soft_delete_room",
        lambda id: fake_room,
    )

    # Act
    response = client.delete(f"/rooms/{fake_room_id}")

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""


def test_delete_room_returns_404_when_not_exists(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_id_including_deleted",
        lambda id: [],
    )

    # Act
    response = client.delete(f"/rooms/{fake_room_id}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room not found"


def test_delete_already_deleted_room_returns_409(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.get_room_by_id_including_deleted",
        lambda id: fake_room,
    )
    monkeypatch.setattr(
        "app.routes.room_routes.room_repository.soft_delete_room",
        lambda id: [],
    )

    # Act
    response = client.delete(f"/rooms/{fake_room_id}")

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Room is already deleted"