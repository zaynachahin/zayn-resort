from fastapi import status
import pytest

# ==================== DADOS / FIXTURES ====================

fake_room_category_id = "00000000-0000-0000-0000-000000000001"

fake_existing_room_category = [
    ("00000000-0000-0000-0000-000000000002",),
]

deleted_room_category = [
    ("00000000-0000-0000-0000-000000000002",),
]

fake_registered_room_category = [
    (
        "00000000-0000-0000-0000-000000000001",
        "Test",
        2,
        300,
    ),
]

expected_room_category = {
    "room_category_id": "00000000-0000-0000-0000-000000000001",
    "name": "Test",
    "capacity": 2,
    "daily_rate": 300,
}

@pytest.fixture
def valid_room_category_payload():
    return {
        "name": "Test",
        "capacity": 2,
        "daily_rate": 200,
    }


# ==================== CREATE ====================

def test_create_room_category_returns_201(monkeypatch, client, valid_room_category_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_category_routes.get_room_category_by_name",
        lambda name: [],
    )
    monkeypatch.setattr(
        "app.routes.room_category_routes.create_room_category",
        lambda name, capacity, daily_rate: fake_room_category_id,
    )

    # Act
    response = client.post("/room-categories", json=valid_room_category_payload)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "Room Category Created"
    assert response.json()["room_category_id"] == fake_room_category_id


def test_create_room_category_returns_409_when_name_exists(monkeypatch, client, valid_room_category_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_category_routes.get_room_category_by_name",
        lambda name: fake_existing_room_category,
    )

    # Act
    response = client.post("/room-categories", json=valid_room_category_payload)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Room Category already exists"


@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("name", ""),
        ("capacity", 0),
        ("capacity", -1),
        ("daily_rate", 0),
        ("daily_rate", -50),
    ],
)
def test_create_room_category_returns_422_for_invalid_field(client, field, invalid_value):
    # Arrange
    payload = {"name": "Test", "capacity": 2, "daily_rate": 200}
    payload[field] = invalid_value

    # Act
    response = client.post("/room-categories", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_room_category_returns_422_when_required_field_missing(client):
    # Arrange
    payload = {"name": "Test", "capacity": 2, "daily_rate": 200}
    del payload["name"]

    # Act
    response = client.post("/room-categories", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# ==================== GET ====================

def test_list_room_categories_returns_200(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_category_routes.list_room_categories",
        lambda: fake_registered_room_category,
    )

    # Act
    response = client.get("/room-categories")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [expected_room_category]


def test_get_room_category_returns_200(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_category_routes.get_room_category_by_id",
        lambda id: fake_registered_room_category,
    )

    # Act
    response = client.get(f"/room-categories/{fake_room_category_id}")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_room_category


def test_get_room_category_returns_404(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_category_routes.get_room_category_by_id",
        lambda id: [],
    )

    # Act
    response = client.get(f"/room-categories/{fake_room_category_id}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room Category not found"


def test_get_room_category_returns_422_when_id_invalid(client):
    # Act
    response = client.get("/room-categories/abc")

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# ==================== PUT ====================

def test_update_room_category_returns_200(monkeypatch, client, valid_room_category_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_category_routes.get_room_category_by_id",
        lambda id: fake_registered_room_category,
    )
    monkeypatch.setattr(
        "app.routes.room_category_routes.get_room_category_by_name_excluding_id",
        lambda name, id: [],
    )
    monkeypatch.setattr(
        "app.routes.room_category_routes.update_room_category",
        lambda id, name, capacity, daily_rate: fake_existing_room_category,
    )

    # Act
    response = client.put(f"/room-categories/{fake_room_category_id}", json=valid_room_category_payload)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Room category updated"


def test_update_room_category_returns_404_when_not_exists(monkeypatch, client, valid_room_category_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_category_routes.get_room_category_by_id",
        lambda id: [],
    )

    # Act
    response = client.put(f"/room-categories/{fake_room_category_id}", json=valid_room_category_payload)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room Category does not exist"


def test_update_room_category_returns_409_when_name_belongs_to_another(monkeypatch, client, valid_room_category_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_category_routes.get_room_category_by_id",
        lambda id: fake_registered_room_category,
    )
    monkeypatch.setattr(
        "app.routes.room_category_routes.get_room_category_by_name_excluding_id",
        lambda name, id: fake_existing_room_category,
    )

    # Act
    response = client.put(f"/room-categories/{fake_room_category_id}", json=valid_room_category_payload)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Room Category exists"


# ==================== PATCH ====================

def test_patch_room_category_returns_200(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_category_routes.get_room_category_by_id",
        lambda id: fake_registered_room_category,
    )
    monkeypatch.setattr(
        "app.routes.room_category_routes.patch_room_category",
        lambda id, fields: fake_existing_room_category,
    )

    # Act
    response = client.patch(f"/room-categories/{fake_room_category_id}", json={"daily_rate": 250})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Room category updated"


def test_patch_room_category_returns_400_when_body_empty(client):
    # Act
    response = client.patch(f"/room-categories/{fake_room_category_id}", json={})

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "No input provided"


def test_patch_room_category_returns_404_when_not_exists(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_category_routes.get_room_category_by_id",
        lambda id: [],
    )

    # Act
    response = client.patch(f"/room-categories/{fake_room_category_id}", json={"daily_rate": 250})

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room Category does not exist"


def test_patch_room_category_returns_409_when_name_belongs_to_another(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_category_routes.get_room_category_by_id",
        lambda id: fake_registered_room_category,
    )
    monkeypatch.setattr(
        "app.routes.room_category_routes.get_room_category_by_name_excluding_id",
        lambda name, id: fake_existing_room_category,
    )

    # Act
    response = client.patch(f"/room-categories/{fake_room_category_id}", json={"name": "Standard"})

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Room Category exists"


# ==================== DELETE ====================

def test_soft_delete_room_category_returns_204(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_category_routes.soft_delete_room_category",
        lambda id: deleted_room_category,
    )

    # Act
    response = client.delete(f"/room-categories/{fake_room_category_id}")

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""


def test_soft_delete_room_category_returns_404(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.room_category_routes.soft_delete_room_category",
        lambda id: [],
    )

    # Act
    response = client.delete(f"/room-categories/{fake_room_category_id}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_soft_delete_room_category_returns_422_when_id_invalid(client):
    # Act
    response = client.delete("/room-categories/abc")

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT