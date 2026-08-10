from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
import pytest


client = TestClient(app)

fake_customer_id = "00000000-0000-0000-0000-000000000001"

non_existent_customer_id = "00000000-0000-0000-0000-000000000002"

fake_customers = [
    (
        "00000000-0000-0000-0000-000000000001",
        "Test User",
        "1999-01-01",
        "11111111111",
        True
    ),
]

fake_existing_customer = [
    ("00000000-0000-0000-0000-000000000001",),
]

another_customer_with_cpf = [
    ("00000000-0000-0000-0000-000000000002",),
] 

expected_customer_response = {
    "customer_id": fake_customer_id,
    "full_name": "Test User",
    "date_of_birth": "1999-01-01",
    "cpf": "11111111111",
    "newsletter_opt_in": True,
}

fake_updated_customer = [
    ("00000000-0000-0000-0000-000000000001",),
]

fake_updated_customer_id = "00000000-0000-0000-0000-000000000001"

def valid_customer_payload():
    return {
        "full_name": "Test User",
        "date_of_birth": "1999-01-01",
        "cpf": "11111111111",
        "newsletter_opt_in": True,
    }

def valid_patch_payload(**overrides):
    return overrides

# ==================== GET ====================

def test_get_customers_returns_200(monkeypatch):
    # Arrange
    monkeypatch.setattr("app.main.list_customers", lambda: fake_customers)

    # Act
    response = client.get("/customers")

    # Assert
    assert response.status_code == status.HTTP_200_OK

def test_get_customers_returns_list(monkeypatch):
    # Arrange 
    monkeypatch.setattr("app.main.list_customers", lambda: fake_customers)
    
    # Act
    response = client.get("/customers")

    # Assert
    assert response.json() == [expected_customer_response]


def test_get_customer_by_id_returns_200(monkeypatch):
    # Arrange
    monkeypatch.setattr("app.main.get_customer_by_id", lambda customer_id: fake_customers)

    # Act
    response = client.get("/customers/d3fac323-9b89-4ec8-b05d-b1ef54e0b0eb")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_customer_response

def test_get_customer_by_id_returns_404(monkeypatch):
    # Arrange
    monkeypatch.setattr("app.main.get_customer_by_id", lambda customer_id: [])

    # Act
    response = client.get("/customers/00000000-0000-0000-0000-000000000000")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Customer not found"

def test_get_customer_by_id_returns_422_when_id_is_invalid():
    # Arrange
    invalid_customer_id = "abc"

    # Act
    response = client.get(f"/customers/{invalid_customer_id}")

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

# ==================== CREATE ====================

def test_create_customer_returns_201_when_cpf_doesnt_exist(monkeypatch):
    # Arrange
    monkeypatch.setattr("app.main.get_customer_by_cpf", lambda cpf: [])

    def fake_create_customer(full_name, date_of_birth, cpf, newsletter_opt_in):
        return fake_customer_id
    
    monkeypatch.setattr("app.main.create_customer", fake_create_customer)

    # Act
    response = client.post("/customers",json=valid_customer_payload())

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "Customer created"
    assert response.json()["customer_id"] == fake_customer_id

@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("date_of_birth", "1999-02-30"),
        ("cpf", "1111111111"),
        ("cpf", "111111111111"),
        ("newsletter_opt_in", "abc"),
        ("full_name", ""),
    ],
)
def test_create_customer_returns_422_for_invalid_field(field, invalid_value):
    # Arrange
    payload = valid_customer_payload()
    payload[field] = invalid_value

    # Act
    response = client.post("/customers", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

def test_create_customer_returns_422_when_required_field_is_missing():
    # Arrange
    payload = valid_customer_payload()
    del payload["cpf"]

    # Act
    response = client.post("/customers",json=payload)

    # Assert 
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

def test_create_customer_returns_409_when_cpf_exists(monkeypatch):
    # Arrange
    monkeypatch.setattr("app.main.get_customer_by_cpf", lambda cpf: fake_existing_customer)
    
    payload = valid_customer_payload()

    # Act
    response = client.post("/customers", json=payload)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "CPF is registered"

# ==================== PUT ====================

def test_update_customer_returns_200_when_customer_exists(monkeypatch):
    # Arrange
    monkeypatch.setattr(
        "app.main.get_customer_by_cpf_excluding_id",
        lambda cpf, customer_id: [],
    )
    monkeypatch.setattr(
        "app.main.update_customer",
        lambda customer_id, full_name, date_of_birth, cpf, newsletter_opt_in: fake_updated_customer,
    )
    payload = valid_customer_payload()
    payload["newsletter_opt_in"] = False

    # Act
    response = client.put(f"/customers/{fake_customer_id}", json=payload)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Customer updated"
    assert response.json()["customer_id"] == fake_updated_customer_id


def test_update_customer_returns_404_when_customer_does_not_exist(monkeypatch):
    # Arrange
    monkeypatch.setattr("app.main.get_customer_by_cpf_excluding_id", lambda cpf, customer_id: [])

    def fake_update_customer(customer_id, full_name, date_of_birth, cpf, newsletter_opt_in):
        return []

    monkeypatch.setattr("app.main.update_customer", fake_update_customer)

    payload = valid_customer_payload()

    # Act
    response = client.put(f"/customers/{non_existent_customer_id}", json=payload)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Customer not found"

def test_update_customer_returns_409_when_cpf_belongs_to_other_customer(monkeypatch):
    # Arrange
    monkeypatch.setattr("app.main.get_customer_by_cpf_excluding_id", lambda cpf, customer_id: fake_existing_customer)

    payload = valid_customer_payload()
    
    # Act
    response = client.put(f"/customers/{fake_customer_id}", json=payload)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "CPF is registered"

def test_update_customer_returns_200_when_customer_keeps_same_cpf(monkeypatch):
    # Arrange
    monkeypatch.setattr("app.main.get_customer_by_cpf_excluding_id", lambda cpf, customer_id: [])

    def fake_update_customer(customer_id, full_name, date_of_birth, cpf, newsletter_opt_in):
        return fake_updated_customer

    monkeypatch.setattr("app.main.update_customer", fake_update_customer)

    payload = valid_customer_payload()
    payload["newsletter_opt_in"] = False

    # Act
    response = client.put(f"/customers/{fake_customer_id}", json=payload)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Customer updated"
    assert response.json()["customer_id"] == fake_updated_customer_id
        
@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("cpf", "1111111111"),
        ("cpf", "111111111111"),
        ("date_of_birth", "1999-02-30"),
        ("newsletter_opt_in", "abc"),
    ],
)
def test_update_customer_returns_422_for_invalid_field(field, invalid_value):
    # Arrange
    payload = valid_customer_payload()
    payload[field] = invalid_value

    # Act
    response = client.put(f"/customers/{fake_customer_id}", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_customer_returns_422_when_required_field_is_missing():
    # Arrange
    payload = valid_customer_payload()
    del payload["cpf"]

    # Act
    response = client.put(f"/customers/{fake_customer_id}", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_customer_returns_422_when_id_is_invalid():
    # Act
    response = client.put("/customers/abc", json=valid_customer_payload())

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

# ==================== PATCH ====================

def _mock_customer_exists(monkeypatch):
    """Helper: simula que o customer existe no banco."""
    monkeypatch.setattr(
        "app.main.get_customer_by_id",
        lambda customer_id: fake_existing_customer,
    )


def test_patch_customer_returns_200_when_partial_update(monkeypatch):
    # Arrange
    _mock_customer_exists(monkeypatch)
    monkeypatch.setattr(
        "app.main.patch_customer",
        lambda customer_id, fields: fake_updated_customer,
    )
    payload = valid_patch_payload(newsletter_opt_in=False)

    # Act
    response = client.patch(f"/customers/{fake_customer_id}", json=payload)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Customer updated"
    assert response.json()["customer_id"] == fake_updated_customer_id


def test_patch_customer_returns_200_when_cpf_has_no_conflict(monkeypatch):
    # Arrange
    _mock_customer_exists(monkeypatch)
    monkeypatch.setattr(
        "app.main.get_customer_by_cpf_excluding_id",
        lambda cpf, customer_id: [],
    )
    monkeypatch.setattr(
        "app.main.patch_customer",
        lambda customer_id, fields: fake_updated_customer,
    )
    payload = valid_patch_payload(cpf="22222222222")

    # Act
    response = client.patch(f"/customers/{fake_customer_id}", json=payload)

    # Assert
    assert response.status_code == status.HTTP_200_OK


def test_patch_customer_returns_400_when_body_is_empty():
    # Arrange
    payload = valid_patch_payload()

    # Act
    response = client.patch(f"/customers/{fake_customer_id}", json=payload)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "No input provided"


def test_patch_customer_returns_404_when_customer_does_not_exist(monkeypatch):
    # Arrange
    monkeypatch.setattr(
        "app.main.get_customer_by_id",
        lambda customer_id: [],
    )
    payload = valid_patch_payload(newsletter_opt_in=True)

    # Act
    response = client.patch(f"/customers/{non_existent_customer_id}", json=payload)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Customer not found"


def test_patch_customer_returns_409_when_cpf_belongs_to_another(monkeypatch):
    # Arrange
    _mock_customer_exists(monkeypatch)
    monkeypatch.setattr(
        "app.main.get_customer_by_cpf_excluding_id",
        lambda cpf, customer_id: another_customer_with_cpf,
    )
    payload = valid_patch_payload(cpf="22222222222")

    # Act
    response = client.patch(f"/customers/{fake_customer_id}", json=payload)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "CPF is registered"


@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("cpf", "1111111111"),
        ("cpf", "111111111111"),
        ("date_of_birth", "1999-02-30"),
        ("newsletter_opt_in", "abc"),
        ("full_name", ""),
    ],
)
def test_patch_customer_returns_422_when_invalid_field(field, invalid_value):
    # Arrange
    payload = {field: invalid_value}

    # Act
    response = client.patch(f"/customers/{fake_customer_id}", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_patch_customer_returns_422_when_id_is_invalid():
    # Arrange
    payload = valid_patch_payload(newsletter_opt_in=True)

    # Act
    response = client.patch("/customers/abc", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT