from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

fake_customer_id = "00000000-0000-0000-0000-000000000001"

fake_customer = [
    (
        "00000000-0000-0000-0000-000000000001",
        "Test User",
        "1999-01-01",
        "11111111111",
        True
    )
]

fake_existing_customer = [
    ("00000000-0000-0000-0000-000000000001",)
]

expected_customer_response = [
    fake_customer_id,
    "Test User",
    "1999-01-01",
    "11111111111",
    True
]

def valid_customer_payload():
    return {
        "full_name": "Test User",
        "date_of_birth": "1999-01-01",
        "cpf": "11111111111",
        "newsletter_opt_in": True
    }

def test_get_customers_returns_200(monkeypatch):
    # Arrange
    def fake_list_customers():
        return fake_customer
    
    monkeypatch.setattr("app.main.list_customers", fake_list_customers)

    # Act
    response = client.get("/customers")

    # Assert
    assert response.status_code == 200

def test_get_customers_returns_list(monkeypatch):
    # Arrange 
    def fake_list_customers():
        return fake_customer
    
    monkeypatch.setattr("app.main.list_customers", fake_list_customers)
    
    # Act
    response = client.get("/customers")

    # Assert
    assert response.json() == expected_customer_response


def test_get_customer_by_id_returns_200(monkeypatch):
    # Arrange
    def fake_get_customer_by_id(customer_id):
        return fake_customer
    
    monkeypatch.setattr("app.main.get_customer_by_id", fake_get_customer_by_id)

    # Act
    response = client.get("/customers/d3fac323-9b89-4ec8-b05d-b1ef54e0b0eb")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_customer_response

def test_get_customer_by_id_returns_404(monkeypatch):
    # Arrange
    def fake_get_customer_by_id(customer_id):
        return []
    
    monkeypatch.setattr("app.main.get_customer_by_id", fake_get_customer_by_id)

    # Act
    response = client.get("/customers/00000000-0000-0000-0000-000000000000")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"

def test_get_customer_by_id_returns_422_when_id_is_invalid():
    # Arrange
    invalid_customer_id = "abc"

    # Act
    response = client.get(f"/customers/{invalid_customer_id}")

    # Assert
    assert response.status_code == 422

def test_create_customer_returns_201_when_cpf_doesnt_exist(monkeypatch):
    # Arrange
    def fake_get_customer_by_cpf(cpf):
        return []
    
    monkeypatch.setattr("app.main.get_customer_by_cpf", fake_get_customer_by_cpf)

    def fake_create_customer(full_name, date_of_birth, cpf, newsletter_opt_in):
        return fake_customer_id
    
    monkeypatch.setattr("app.main.create_customer", fake_create_customer)

    # Act
    response = client.post("/customers",json=valid_customer_payload())

    # Assert
    assert response.status_code == 201
    assert response.json()["message"] == "Customer created"
    assert response.json()["customer_id"] == fake_customer_id

def test_create_customer_returns_422_when_invalid_date():
    # Arrange
    payload = valid_customer_payload()
    payload["date_of_birth"] = "1999-02-30"

    # Act
    response = client.post("/customers",json=payload)

    # Assert 
    assert response.status_code == 422

def test_create_customer_returns_422_when_cpf_is_too_short():
    # Arrange
    payload = valid_customer_payload()
    payload["cpf"] = "1111111111"

    # Act
    response = client.post("/customers",json=payload)

    # Assert 
    assert response.status_code == 422

def test_create_customer_returns_422_when_cpf_is_too_long():
    # Arrange
    payload = valid_customer_payload()
    payload["cpf"] = "111111111111"

    # Act
    response = client.post("/customers",json=payload)

    # Assert 
    assert response.status_code == 422

def test_create_customer_returns_422_when_invalid_newsletter_opt_in():
    # Arrange
    payload = valid_customer_payload()
    payload["newsletter_opt_in"] = "abc"

    # Act
    response = client.post("/customers",json=payload)

    # Assert 
    assert response.status_code == 422

def test_create_customer_returns_422_when_required_field_is_missing():
    # Arrange
    payload = valid_customer_payload()
    del payload["cpf"]

    # Act
    response = client.post("/customers",json=payload)

    # Assert 
    assert response.status_code == 422

def test_create_customer_returns_409_when_cpf_exists(monkeypatch):
    # Arrange
    def fake_get_customer_by_cpf(cpf):
        return fake_existing_customer
    
    monkeypatch.setattr("app.main.get_customer_by_cpf", fake_get_customer_by_cpf)
    
    payload = valid_customer_payload()

    # Act
    response = client.post("/customers", json=payload)

    # Assert
    assert response.status_code == 409
    assert response.json()["detail"] == "CPF is registered"