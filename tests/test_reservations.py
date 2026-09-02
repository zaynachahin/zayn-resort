from fastapi import status
from decimal import Decimal
import pytest

# ==================== FAKE DATA ====================

fake_reservation_id = "00000000-0000-0000-0000-000000000001"

fake_reservation = [(
    "00000000-0000-0000-0000-000000000001",
    "00000000-0000-0000-0000-000000000002",
    "00000000-0000-0000-0000-000000000003",
    "2027-01-26",
    "2027-02-04",
    "confirmed",
    "2700.00",
)]

fake_customer = [("Test Customer",)]

fake_room = [(
    "00000000-0000-0000-0000-000000000003",
    "101",
    "Test Room",
    "Test Description",
    "00000000-0000-0000-0000-000000000004",
)]

fake_room_category = [(
    "00000000-0000-0000-0000-000000000004",
    "Test Category",
    2,
    Decimal("300"),
)]

expected_reservation = {
    "reservation_id": "00000000-0000-0000-0000-000000000001",
    "customer_id": "00000000-0000-0000-0000-000000000002",
    "room_id": "00000000-0000-0000-0000-000000000003",
    "check_in": "2027-01-26",
    "check_out": "2027-02-04",
    "status": "confirmed",
    "total_amount": "2700.00",
}

@pytest.fixture
def valid_reservation_payload():
    return {
        "customer_id": "00000000-0000-0000-0000-000000000002",
        "room_id": "00000000-0000-0000-0000-000000000003",
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
    monkeypatch.setattr("app.services.reservation_service.get_customer_by_id", lambda customer_id: fake_customer)
    monkeypatch.setattr("app.services.reservation_service.get_room_by_id", lambda room_id: fake_room)
    monkeypatch.setattr("app.services.reservation_service.get_room_category_by_id", lambda room_category_id: fake_room_category)
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_conflicting_reservations", lambda room_id, check_out, check_in: [])
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.create_reservation", lambda customer_id, room_id, check_in, check_out, total_amount: fake_reservation_id)

    response = client.post("/reservations", json=valid_reservation_payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["reservation_id"] == fake_reservation_id


def test_create_reservation_returns_404_when_customer_not_found(monkeypatch, client, valid_reservation_payload):
    monkeypatch.setattr("app.services.reservation_service.get_customer_by_id", lambda customer_id: [])

    response = client.post("/reservations", json=valid_reservation_payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Customer not found"


def test_create_reservation_returns_404_when_room_not_found(monkeypatch, client, valid_reservation_payload):
    monkeypatch.setattr("app.services.reservation_service.get_customer_by_id", lambda customer_id: fake_customer)
    monkeypatch.setattr("app.services.reservation_service.get_room_by_id", lambda room_id: [])

    response = client.post("/reservations", json=valid_reservation_payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room not found"


def test_create_reservation_returns_409_when_room_not_available(monkeypatch, client, valid_reservation_payload):
    monkeypatch.setattr("app.services.reservation_service.get_customer_by_id", lambda customer_id: fake_customer)
    monkeypatch.setattr("app.services.reservation_service.get_room_by_id", lambda room_id: fake_room)
    monkeypatch.setattr("app.services.reservation_service.get_room_category_by_id", lambda room_category_id: fake_room_category)
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_conflicting_reservations", lambda room_id, check_out, check_in: [("conflict",)])

    response = client.post("/reservations", json=valid_reservation_payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Room not available"


@pytest.mark.parametrize("field, value", [
    ("check_in", "abc"),
    ("check_out", "abc"),
    ("customer_id", "not-a-uuid"),
    ("room_id", "not-a-uuid"),
])
def test_create_reservation_returns_422_for_invalid_field(client, valid_reservation_payload, field, value):
    valid_reservation_payload[field] = value
    response = client.post("/reservations", json=valid_reservation_payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize("field", ["customer_id", "room_id", "check_in", "check_out"])
def test_create_reservation_returns_422_when_field_is_missing(client, valid_reservation_payload, field):
    del valid_reservation_payload[field]
    response = client.post("/reservations", json=valid_reservation_payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_reservation_returns_422_when_checkout_before_checkin(client, valid_reservation_payload):
    valid_reservation_payload["check_out"] = "2027-01-22"
    response = client.post("/reservations", json=valid_reservation_payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# ==================== GET ====================

def test_get_reservation_returns_200(monkeypatch, client):
    monkeypatch.setattr("app.routes.reservation_routes.reservation_repository.get_reservation_by_id", lambda id: fake_reservation)

    response = client.get(f"/reservations/{fake_reservation_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_reservation


def test_get_reservation_returns_404(monkeypatch, client):
    monkeypatch.setattr("app.routes.reservation_routes.reservation_repository.get_reservation_by_id", lambda id: [])

    response = client.get(f"/reservations/{fake_reservation_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Reservation not found"


def test_get_reservation_returns_422_when_id_invalid(client):
    response = client.get("/reservations/abc")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_list_reservations_returns_200(monkeypatch, client):
    monkeypatch.setattr("app.routes.reservation_routes.reservation_repository.list_reservations", lambda: fake_reservation)

    response = client.get("/reservations")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [expected_reservation]


def test_list_reservations_returns_empty_list(monkeypatch, client):
    monkeypatch.setattr("app.routes.reservation_routes.reservation_repository.list_reservations", lambda: [])

    response = client.get("/reservations")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


# ==================== PATCH DATES ====================

def test_update_reservation_dates_returns_200(monkeypatch, client, valid_dates_payload):
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: fake_reservation)
    monkeypatch.setattr("app.services.reservation_service.get_room_by_id", lambda room_id: fake_room)
    monkeypatch.setattr("app.services.reservation_service.get_room_category_by_id", lambda room_category_id: fake_room_category)
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_conflicting_reservations_excluding_id", lambda room_id, id, check_out, check_in: [])
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.update_reservation_dates", lambda id, check_in, check_out, total_amount: fake_reservation_id)

    response = client.patch(f"/reservations/{fake_reservation_id}/dates", json=valid_dates_payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["reservation_id"] == fake_reservation_id


def test_update_reservation_dates_returns_404(monkeypatch, client, valid_dates_payload):
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: [])

    response = client.patch(f"/reservations/{fake_reservation_id}/dates", json=valid_dates_payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Reservation not found"


def test_update_reservation_dates_returns_409_when_room_not_available(monkeypatch, client, valid_dates_payload):
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: fake_reservation)
    monkeypatch.setattr("app.services.reservation_service.get_room_by_id", lambda room_id: fake_room)
    monkeypatch.setattr("app.services.reservation_service.get_room_category_by_id", lambda room_category_id: fake_room_category)
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_conflicting_reservations_excluding_id", lambda room_id, id, check_out, check_in: [("conflict",)])

    response = client.patch(f"/reservations/{fake_reservation_id}/dates", json=valid_dates_payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Room not available"


@pytest.mark.parametrize("cancelled_or_checked_out", ["cancelled", "checked_out"])
def test_update_reservation_dates_returns_409_when_status_blocks_update(monkeypatch, client, valid_dates_payload, cancelled_or_checked_out):
    blocked_reservation = [(
        "00000000-0000-0000-0000-000000000001",
        "00000000-0000-0000-0000-000000000002",
        "00000000-0000-0000-0000-000000000003",
        "2027-01-26",
        "2027-02-04",
        cancelled_or_checked_out,
        "2700.00",
    )]
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: blocked_reservation)

    response = client.patch(f"/reservations/{fake_reservation_id}/dates", json=valid_dates_payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Cannot update dates of a cancelled or checked_out reservation"


def test_update_reservation_dates_returns_422_when_checkout_before_checkin(client):
    payload = {"check_in": "2027-03-10", "check_out": "2027-03-01"}
    response = client.patch(f"/reservations/{fake_reservation_id}/dates", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# ==================== PATCH STATUS ====================

def test_update_reservation_status_returns_200(monkeypatch, client):
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: fake_reservation)
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.update_reservation_status", lambda id, status: fake_reservation_id)

    response = client.patch(f"/reservations/{fake_reservation_id}/status", json={"status": "checked_in"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["reservation_id"] == fake_reservation_id


def test_update_reservation_status_returns_404(monkeypatch, client):
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: [])

    response = client.patch(f"/reservations/{fake_reservation_id}/status", json={"status": "checked_in"})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Reservation not found"


@pytest.mark.parametrize("old_status, new_status", [
    ("confirmed", "checked_out"),
    ("checked_in", "cancelled"),
    ("checked_in", "confirmed"),
    ("checked_out", "confirmed"),
    ("checked_out", "checked_in"),
    ("checked_out", "cancelled"),
    ("cancelled", "checked_out"),
    ("cancelled", "confirmed"),
    ("cancelled", "checked_in"),
])
def test_update_reservation_status_returns_409_for_invalid_transition(monkeypatch, client, old_status, new_status):
    blocked_reservation = [(
        "00000000-0000-0000-0000-000000000001",
        "00000000-0000-0000-0000-000000000002",
        "00000000-0000-0000-0000-000000000003",
        "2027-01-26",
        "2027-02-04",
        old_status,
        "2700.00",
    )]
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: blocked_reservation)

    response = client.patch(f"/reservations/{fake_reservation_id}/status", json={"status": new_status})

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Cannot change status"


# ==================== DELETE ====================

def test_delete_reservation_returns_204(monkeypatch, client):
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: fake_reservation)
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.soft_delete_reservation", lambda id: fake_reservation_id)

    response = client.delete(f"/reservations/{fake_reservation_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""


def test_delete_reservation_returns_404(monkeypatch, client):
    monkeypatch.setattr("app.services.reservation_service.reservation_repository.get_reservation_by_id", lambda id: [])

    response = client.delete(f"/reservations/{fake_reservation_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Reservation not found"


def test_delete_reservation_returns_422_when_id_invalid(client):
    response = client.delete("/reservations/abc")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT