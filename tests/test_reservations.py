# ==================== test_reservations.py ====================

from fastapi import status
from decimal import Decimal
import pytest

# ==================== DADOS / FIXTURES ====================

fake_reservation_id = "00000000-0000-0000-0000-000000000001"
fake_customer_id = "00000000-0000-0000-0000-000000000002"
fake_room_id = "00000000-0000-0000-0000-000000000003"
fake_category_id = "00000000-0000-0000-0000-000000000004"

fake_reservation_row = {
    "id": fake_reservation_id,
    "customer_id": fake_customer_id,
    "room_id": fake_room_id,
    "check_in": "2027-01-26",
    "check_out": "2027-02-04",
    "status": "confirmed",
    "total_amount": "2700.00",
}

fake_customer = {"id": fake_customer_id}

fake_room_row = {
    "id": fake_room_id,
    "number": "101",
    "name": "Test Room",
    "description": "Test Description",
    "room_category_id": fake_category_id,
}

fake_room_category_row = {
    "id": fake_category_id,
    "name": "Test Category",
    "capacity": 2,
    "daily_rate": Decimal("300"),
}

expected_reservation_get_response = {
    "reservation_id": fake_reservation_id,
    "customer_id": fake_customer_id,
    "room_id": fake_room_id,
    "check_in": "2027-01-26",
    "check_out": "2027-02-04",
    "status": "confirmed",
    "total_amount": "2700.00",
}

fake_created_reservation = {
    **fake_reservation_row,
    "created_at": "2024-01-01T00:00:00",
}

fake_updated_reservation = {
    **fake_reservation_row,
    "updated_at": "2024-01-02T00:00:00",
}


def make_reservation_with_status(status_value):
    return {**fake_reservation_row, "status": status_value}


@pytest.fixture
def valid_reservation_payload():
    return {
        "customer_id": fake_customer_id,
        "room_id": fake_room_id,
        "check_in": "2027-01-26",
        "check_out": "2027-02-04",
    }


@pytest.fixture
def valid_dates_payload():
    return {
        "check_in": "2027-03-01",
        "check_out": "2027-03-10",
    }


# ==================== CREATE ====================

def test_create_reservation_returns_201(monkeypatch, client, valid_reservation_payload):
    # Arrange
    monkeypatch.setattr("app.services.reservation_service.get_customer_by_id", lambda customer_id: fake_customer)
    monkeypatch.setattr("app.services.reservation_service.get_room_by_id", lambda room_id: fake_room_row)
    monkeypatch.setattr("app.services.reservation_service.get_room_category_by_id", lambda room_category_id: fake_room_category_row)
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_conflicting_reservations", lambda room_id, check_out, check_in: [])
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.create_reservation", lambda customer_id, room_id, check_in, check_out, total_amount: fake_created_reservation)

    # Act
    response = client.post("/reservations", json=valid_reservation_payload)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == fake_created_reservation


def test_create_reservation_returns_404_when_customer_not_found(monkeypatch, client, valid_reservation_payload):
    # Arrange
    monkeypatch.setattr("app.services.reservation_service.get_customer_by_id", lambda customer_id: None)

    # Act
    response = client.post("/reservations", json=valid_reservation_payload)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Customer not found"


def test_create_reservation_returns_404_when_room_not_found(monkeypatch, client, valid_reservation_payload):
    # Arrange
    monkeypatch.setattr("app.services.reservation_service.get_customer_by_id", lambda customer_id: fake_customer)
    monkeypatch.setattr("app.services.reservation_service.get_room_by_id", lambda room_id: None)

    # Act
    response = client.post("/reservations", json=valid_reservation_payload)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room not found"


def test_create_reservation_returns_409_when_room_not_available(monkeypatch, client, valid_reservation_payload):
    # Arrange
    monkeypatch.setattr("app.services.reservation_service.get_customer_by_id", lambda customer_id: fake_customer)
    monkeypatch.setattr("app.services.reservation_service.get_room_by_id", lambda room_id: fake_room_row)
    monkeypatch.setattr("app.services.reservation_service.get_room_category_by_id", lambda room_category_id: fake_room_category_row)
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_conflicting_reservations", lambda room_id, check_out, check_in: [{"id": "conflict"}])

    # Act
    response = client.post("/reservations", json=valid_reservation_payload)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Room not available"


@pytest.mark.parametrize(
    "field, value",
    [
        ("check_in", "abc"),
        ("check_out", "abc"),
        ("customer_id", "not-a-uuid"),
        ("room_id", "not-a-uuid"),
    ],
)
def test_create_reservation_returns_422_for_invalid_field(client, valid_reservation_payload, field, value):
    # Arrange
    payload = valid_reservation_payload.copy()
    payload[field] = value

    # Act
    response = client.post("/reservations", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize("field", ["customer_id", "room_id", "check_in", "check_out"])
def test_create_reservation_returns_422_when_field_is_missing(client, valid_reservation_payload, field):
    # Arrange
    payload = valid_reservation_payload.copy()
    del payload[field]

    # Act
    response = client.post("/reservations", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_reservation_returns_422_when_checkout_before_checkin(client, valid_reservation_payload):
    # Arrange
    payload = valid_reservation_payload.copy()
    payload["check_out"] = "2027-01-22"

    # Act
    response = client.post("/reservations", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# ==================== GET ====================

def test_get_reservation_returns_200(monkeypatch, client):
    # Arrange
    monkeypatch.setattr("app.routes.reservation_routes.reservation_repository.get_reservation_by_id", lambda id: fake_reservation_row)

    # Act
    response = client.get(f"/reservations/{fake_reservation_id}")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_reservation_get_response


def test_get_reservation_returns_404(monkeypatch, client):
    # Arrange
    monkeypatch.setattr("app.routes.reservation_routes.reservation_repository.get_reservation_by_id", lambda id: None)

    # Act
    response = client.get(f"/reservations/{fake_reservation_id}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Reservation not found"


def test_get_reservation_returns_422_when_id_invalid(client):
    # Act
    response = client.get("/reservations/abc")

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_list_reservations_returns_200(monkeypatch, client):
    # Arrange
    monkeypatch.setattr("app.routes.reservation_routes.reservation_repository.list_reservations", lambda: [fake_reservation_row])

    # Act
    response = client.get("/reservations")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [expected_reservation_get_response]


def test_list_reservations_returns_empty_list(monkeypatch, client):
    # Arrange
    monkeypatch.setattr("app.routes.reservation_routes.reservation_repository.list_reservations", lambda: [])

    # Act
    response = client.get("/reservations")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


# ==================== PATCH DATES ====================

def test_update_reservation_dates_returns_200(monkeypatch, client, valid_dates_payload):
    # Arrange
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: fake_reservation_row)
    monkeypatch.setattr("app.services.reservation_service.get_room_by_id", lambda room_id: fake_room_row)
    monkeypatch.setattr("app.services.reservation_service.get_room_category_by_id", lambda room_category_id: fake_room_category_row)
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_conflicting_reservations_excluding_id", lambda room_id, id, check_out, check_in: [])
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.update_reservation_dates", lambda id, check_in, check_out, total_amount: fake_updated_reservation)

    # Act
    response = client.patch(f"/reservations/{fake_reservation_id}/dates", json=valid_dates_payload)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == fake_updated_reservation


def test_update_reservation_dates_returns_404(monkeypatch, client, valid_dates_payload):
    # Arrange
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: None)

    # Act
    response = client.patch(f"/reservations/{fake_reservation_id}/dates", json=valid_dates_payload)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Reservation not found"


def test_update_reservation_dates_returns_409_when_room_not_available(monkeypatch, client, valid_dates_payload):
    # Arrange
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: fake_reservation_row)
    monkeypatch.setattr("app.services.reservation_service.get_room_by_id", lambda room_id: fake_room_row)
    monkeypatch.setattr("app.services.reservation_service.get_room_category_by_id", lambda room_category_id: fake_room_category_row)
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_conflicting_reservations_excluding_id", lambda room_id, id, check_out, check_in: [{"id": "conflict"}])

    # Act
    response = client.patch(f"/reservations/{fake_reservation_id}/dates", json=valid_dates_payload)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Room not available"


@pytest.mark.parametrize("blocking_status", ["cancelled", "checked_out"])
def test_update_reservation_dates_returns_409_when_status_blocks_update(monkeypatch, client, valid_dates_payload, blocking_status):
    # Arrange
    blocked_reservation = make_reservation_with_status(blocking_status)
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: blocked_reservation)

    # Act
    response = client.patch(f"/reservations/{fake_reservation_id}/dates", json=valid_dates_payload)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Cannot update dates of a cancelled or checked_out reservation"


def test_update_reservation_dates_returns_422_when_checkout_before_checkin(client):
    # Arrange
    payload = {"check_in": "2027-03-10", "check_out": "2027-03-01"}

    # Act
    response = client.patch(f"/reservations/{fake_reservation_id}/dates", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# ==================== PATCH STATUS ====================

def test_update_reservation_status_returns_200(monkeypatch, client):
    # Arrange
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: fake_reservation_row)
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.update_reservation_status", lambda id, status: fake_updated_reservation)

    # Act
    response = client.patch(f"/reservations/{fake_reservation_id}/status", json={"status": "checked_in"})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == fake_updated_reservation


def test_update_reservation_status_returns_404(monkeypatch, client):
    # Arrange
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: None)

    # Act
    response = client.patch(f"/reservations/{fake_reservation_id}/status", json={"status": "checked_in"})

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Reservation not found"


@pytest.mark.parametrize(
    "old_status, new_status",
    [
        ("confirmed", "checked_out"),
        ("checked_in", "cancelled"),
        ("checked_in", "confirmed"),
        ("checked_out", "confirmed"),
        ("checked_out", "checked_in"),
        ("checked_out", "cancelled"),
        ("cancelled", "checked_out"),
        ("cancelled", "confirmed"),
        ("cancelled", "checked_in"),
    ],
)
def test_update_reservation_status_returns_409_for_invalid_transition(monkeypatch, client, old_status, new_status):
    # Arrange
    blocked_reservation = make_reservation_with_status(old_status)
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: blocked_reservation)

    # Act
    response = client.patch(f"/reservations/{fake_reservation_id}/status", json={"status": new_status})

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Cannot change status"


# ==================== DELETE ====================

def test_delete_reservation_returns_204(monkeypatch, client):
    # Arrange
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id_including_deleted", lambda id: fake_reservation_row)
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.soft_delete_reservation", lambda id: {"id": fake_reservation_id, "deleted_at": "2024-01-03T00:00:00"})

    # Act
    response = client.delete(f"/reservations/{fake_reservation_id}")

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""


def test_delete_reservation_returns_404_when_not_exists(monkeypatch, client):
    # Arrange
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id_including_deleted", lambda id: None)

    # Act
    response = client.delete(f"/reservations/{fake_reservation_id}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Reservation not found"


def test_delete_reservation_returns_409_when_already_deleted(monkeypatch, client):
    # Arrange
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id_including_deleted", lambda id: fake_reservation_row)
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.soft_delete_reservation", lambda id: None)

    # Act
    response = client.delete(f"/reservations/{fake_reservation_id}")

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Reservation is already deleted"