
import pytest
from fastapi.testclient import TestClient

from app import database
from app.auth import hash_password, create_token
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_dealership.db"
    monkeypatch.setattr(database, "DATABASE_PATH", test_db)
    monkeypatch.setenv("JWT_SECRET", "test-secret-for-tests-only")

    with TestClient(app) as test_client:
        with database.get_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, 'admin')
                """,
                ("testadmin", hash_password("adminpass123")),
            )

        yield test_client


def get_admin_token():
    return create_token("testadmin", "admin")


def create_vehicle(client, make="Toyota", model="Corolla",
                   category="Sedan", price=25000, quantity=5):
    return client.post(
        "/api/vehicles",
        json={
            "make": make,
            "model": model,
            "category": category,
            "price": price,
            "quantity": quantity,
        },
        headers={"Authorization": f"Bearer {get_admin_token()}"},
    )


def test_list_vehicles_returns_empty_list(client):
    response = client.get("/api/vehicles")
    assert response.status_code == 200
    assert response.json() == []


def test_create_vehicle(client):
    response = create_vehicle(client)

    assert response.status_code == 201
    assert response.json()["make"] == "Toyota"
    assert response.json()["quantity"] == 5
    assert "id" in response.json()


def test_search_vehicles_by_make(client):
    create_vehicle(client)
    create_vehicle(client, make="Honda", model="Civic", price=22000,
                   quantity=3)

    response = client.get("/api/vehicles/search?make=Toyota")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["model"] == "Corolla"


def test_update_vehicle(client):
    vehicle_id = create_vehicle(client).json()["id"]

    response = client.put(
        f"/api/vehicles/{vehicle_id}",
        json={
            "make": "Toyota",
            "model": "Camry",
            "category": "Sedan",
            "price": 30000,
            "quantity": 4,
        },
        headers={"Authorization": f"Bearer {get_admin_token()}"},
    )

    assert response.status_code == 200
    assert response.json()["model"] == "Camry"
    assert response.json()["price"] == 30000
    assert response.json()["quantity"] == 4


def test_delete_vehicle(client):
    vehicle_id = create_vehicle(client).json()["id"]

    response = client.delete(
        f"/api/vehicles/{vehicle_id}",
        headers={"Authorization": f"Bearer {get_admin_token()}"},
    )

    assert response.status_code == 204
    vehicles = client.get("/api/vehicles").json()
    assert all(vehicle["id"] != vehicle_id for vehicle in vehicles)


def test_delete_nonexistent_vehicle_returns_404(client):
    response = client.delete(
        "/api/vehicles/9999",
        headers={"Authorization": f"Bearer {get_admin_token()}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Vehicle not found"


def test_purchase_vehicle_reduces_quantity(client):
    vehicle_id = create_vehicle(client, quantity=2).json()["id"]
    token = create_token("testuser", "user")

    response = client.post(
        f"/api/vehicles/{vehicle_id}/purchase",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 1


def test_purchase_vehicle_out_of_stock_returns_409(client):
    vehicle_id = create_vehicle(client, quantity=0).json()["id"]
    token = create_token("testuser", "user")

    response = client.post(
        f"/api/vehicles/{vehicle_id}/purchase",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Vehicle is out of stock"


def test_purchase_without_token_returns_401(client):
    vehicle_id = create_vehicle(
        client, make="Honda", model="Civic", quantity=3
    ).json()["id"]

    response = client.post(f"/api/vehicles/{vehicle_id}/purchase")

    assert response.status_code == 401


def test_admin_can_restock_vehicle(client):
    vehicle_id = create_vehicle(client, quantity=2).json()["id"]

    response = client.post(
        f"/api/vehicles/{vehicle_id}/restock",
        json={"quantity": 3},
        headers={"Authorization": f"Bearer {get_admin_token()}"},
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 5


def test_regular_user_cannot_restock_vehicle(client):
    vehicle_id = create_vehicle(
        client, make="Honda", model="Civic", quantity=2
    ).json()["id"]
    token = create_token("testuser", "user")

    response = client.post(
        f"/api/vehicles/{vehicle_id}/restock",
        json={"quantity": 3},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"
