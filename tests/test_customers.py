from fastapi import status
import pytest

# ==================== DADOS / FIXTURES ====================

fake_customer_id = "00000000-0000-0000-0000-000000000001"
non_existent_customer_id = "00000000-0000-0000-0000-000000000002"

fake_customers = [
    (
        "00000000-0000-0000-0000-000000000001",
        "Test User",
        "1999-01-01",
        "11111111111",
        True,
    ),
]

fake_existing_customer = [
    ("00000000-0000-0000-0000-000000000001",),
]

another_customer_with_cpf = [
    ("00000000-0000-0000-0000-000000000002",),
]

fake_updated_customer = [
    ("00000000-0000-0000-0000-000000000001",),
]

fake_deleted_customer = [
    ("00000000-0000-0000-0000-000000000001",),
]

expected_customer_response = {
    "customer_id": "00000000-0000-0000-0000-000000000001",
    "full_name": "Test User",
    "date_of_birth": "1999-01-01",
    "cpf": "11111111111",
    "newsletter_opt_in": True,
}

@pytest.fixture
def valid_customer_payload():
    return {
        "full_name": "Test User",
        "date_of_birth": "1999-01-01",
        "cpf": "11111111111",
        "newsletter_opt_in": True,
    }


# ==================== GET ====================

def test_get_customers_returns_200(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.customer_routes.list_customers",
        lambda: fake_customers,
    )

    # Act
    response = client.get("/customers")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [expected_customer_response]


def test_get_customer_by_id_returns_200(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.customer_routes.get_customer_by_id",
        lambda customer_id: fake_customers,
    )

    # Act
    response = client.get(f"/customers/{fake_customer_id}")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_customer_response


def test_get_customer_by_id_returns_404(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.customer_routes.get_customer_by_id",
        lambda customer_id: [],
    )

    # Act
    response = client.get(f"/customers/{non_existent_customer_id}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Customer not found"


def test_get_customer_by_id_returns_422_when_id_is_invalid(client):
    # Act
    response = client.get("/customers/abc")

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# ==================== CREATE ====================

def test_create_customer_returns_201_when_cpf_doesnt_exist(monkeypatch, client, valid_customer_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.customer_routes.get_customer_by_cpf",
        lambda cpf: [],
    )
    monkeypatch.setattr(
        "app.routes.customer_routes.create_customer",
        lambda full_name, date_of_birth, cpf, newsletter_opt_in: fake_customer_id,
    )

    # Act
    response = client.post("/customers", json=valid_customer_payload)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "Customer created"
    assert response.json()["customer_id"] == fake_customer_id


def test_create_customer_returns_409_when_cpf_exists(monkeypatch, client, valid_customer_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.customer_routes.get_customer_by_cpf",
        lambda cpf: fake_existing_customer,
    )

    # Act
    response = client.post("/customers", json=valid_customer_payload)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "CPF is registered"


def test_create_customer_returns_422_when_required_field_is_missing(client, valid_customer_payload):
    # Arrange
    payload = valid_customer_payload.copy()
    del payload["cpf"]

    # Act
    response = client.post("/customers", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


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
def test_create_customer_returns_422_for_invalid_field(client, field, invalid_value, valid_customer_payload):
    # Arrange
    payload = valid_customer_payload.copy()
    payload[field] = invalid_value

    # Act
    response = client.post("/customers", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# ==================== PUT ====================

def test_update_customer_returns_200(monkeypatch, client, valid_customer_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.customer_routes.get_customer_by_cpf_excluding_id",
        lambda cpf, customer_id: [],
    )
    monkeypatch.setattr(
        "app.routes.customer_routes.update_customer",
        lambda customer_id, full_name, date_of_birth, cpf, newsletter_opt_in: fake_updated_customer,
    )

    # Act
    response = client.put(f"/customers/{fake_customer_id}", json=valid_customer_payload)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Customer updated"
    assert response.json()["customer_id"] == fake_customer_id


def test_update_customer_returns_404_when_not_exists(monkeypatch, client, valid_customer_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.customer_routes.get_customer_by_cpf_excluding_id",
        lambda cpf, customer_id: [],
    )
    monkeypatch.setattr(
        "app.routes.customer_routes.update_customer",
        lambda customer_id, full_name, date_of_birth, cpf, newsletter_opt_in: [],
    )

    # Act
    response = client.put(f"/customers/{non_existent_customer_id}", json=valid_customer_payload)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Customer not found"


def test_update_customer_returns_409_when_cpf_belongs_to_another(monkeypatch, client, valid_customer_payload):
    # Arrange
    monkeypatch.setattr(
        "app.routes.customer_routes.get_customer_by_cpf_excluding_id",
        lambda cpf, customer_id: fake_existing_customer,
    )

    # Act
    response = client.put(f"/customers/{fake_customer_id}", json=valid_customer_payload)

    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "CPF is registered"


def test_update_customer_returns_422_when_required_field_missing(client, valid_customer_payload):
    # Arrange
    payload = valid_customer_payload.copy()
    del payload["cpf"]

    # Act
    response = client.put(f"/customers/{fake_customer_id}", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("cpf", "1111111111"),
        ("cpf", "111111111111"),
        ("date_of_birth", "1999-02-30"),
        ("newsletter_opt_in", "abc"),
    ],
)
def test_update_customer_returns_422_for_invalid_field(client, field, invalid_value, valid_customer_payload):
    # Arrange
    payload = valid_customer_payload.copy()
    payload[field] = invalid_value

    # Act
    response = client.put(f"/customers/{fake_customer_id}", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_customer_returns_422_when_id_is_invalid(client, valid_customer_payload):
    # Act
    response = client.put("/customers/abc", json=valid_customer_payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# ==================== PATCH ====================

def test_patch_customer_returns_200(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.customer_routes.get_customer_by_id",
        lambda customer_id: fake_existing_customer,
    )
    monkeypatch.setattr(
        "app.routes.customer_routes.patch_customer",
        lambda customer_id, fields: fake_updated_customer,
    )

    # Act
    response = client.patch(f"/customers/{fake_customer_id}", json={"newsletter_opt_in": False})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Customer updated"
    assert response.json()["customer_id"] == fake_customer_id


def test_patch_customer_returns_400_when_body_is_empty(client):
    # Act
    response = client.patch(f"/customers/{fake_customer_id}", json={})

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "No input provided"


def test_patch_customer_returns_404_when_not_exists(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.customer_routes.get_customer_by_id",
        lambda customer_id: [],
    )

    # Act
    response = client.patch(f"/customers/{non_existent_customer_id}", json={"newsletter_opt_in": True})

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Customer not found"


def test_patch_customer_returns_409_when_cpf_belongs_to_another(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.customer_routes.get_customer_by_id",
        lambda customer_id: fake_existing_customer,
    )
    monkeypatch.setattr(
        "app.routes.customer_routes.get_customer_by_cpf_excluding_id",
        lambda cpf, customer_id: another_customer_with_cpf,
    )

    # Act
    response = client.patch(f"/customers/{fake_customer_id}", json={"cpf": "22222222222"})

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
def test_patch_customer_returns_422_for_invalid_field(client, field, invalid_value):
    # Act
    response = client.patch(f"/customers/{fake_customer_id}", json={field: invalid_value})

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_patch_customer_returns_422_when_id_is_invalid(client):
    # Act
    response = client.patch("/customers/abc", json={"newsletter_opt_in": True})

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# ==================== DELETE ====================

def test_delete_customer_returns_204(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.customer_routes.soft_delete_customer",
        lambda customer_id: fake_deleted_customer,
    )

    # Act
    response = client.delete(f"/customers/{fake_customer_id}")

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""


def test_delete_customer_returns_404_when_not_exists(monkeypatch, client):
    # Arrange
    monkeypatch.setattr(
        "app.routes.customer_routes.soft_delete_customer",
        lambda customer_id: [],
    )

    # Act
    response = client.delete(f"/customers/{non_existent_customer_id}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Customer not found or customer is deactivated"


def test_delete_customer_returns_422_when_id_is_invalid(client):
    # Act
    response = client.delete("/customers/abc")

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT