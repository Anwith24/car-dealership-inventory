
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import sqlite3
from app.auth import hash_password
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth import verify_token
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.database import create_tables, get_connection

app = FastAPI(title="Car Dealership Inventory API")

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        return verify_token(credentials.credentials)
    except (ValueError, RuntimeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_admin(
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return current_user


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)



@app.on_event("startup")
def startup():
    create_tables()


@app.post("/api/auth/register", status_code=201)
def register_user(user: UserRegister):
    password_hash = hash_password(user.password)

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, 'user')
                """,
                (user.username, password_hash),
            )

            user_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )

    return {
        "id": user_id,
        "username": user.username,
        "role": "user",
    }


class RestockRequest(BaseModel):
    quantity: int = Field(gt=0)



class VehicleCreate(BaseModel):
    make: str = Field(min_length=1)
    model: str = Field(min_length=1)
    category: str = Field(min_length=1)
    price: float = Field(ge=0)
    quantity: int = Field(ge=0)


@app.get("/api/vehicles")
def list_vehicles():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM vehicles ORDER BY id"
        ).fetchall()

    return [dict(row) for row in rows]


@app.get("/api/vehicles/search")
def search_vehicles(
    make: str | None = None,
    model: str | None = None,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
):
    query = "SELECT * FROM vehicles WHERE 1=1"
    params = []

    if make:
        query += " AND make LIKE ?"
        params.append(f"%{make}%")

    if model:
        query += " AND model LIKE ?"
        params.append(f"%{model}%")

    if category:
        query += " AND category LIKE ?"
        params.append(f"%{category}%")

    if min_price is not None:
        query += " AND price >= ?"
        params.append(min_price)

    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)

    query += " ORDER BY id"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

    return [dict(row) for row in rows]


@app.post("/api/vehicles", status_code=201)
def create_vehicle(
    vehicle: VehicleCreate,
    admin: dict = Depends(require_admin),
):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO vehicles (make, model, category, price, quantity)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                vehicle.make,
                vehicle.model,
                vehicle.category,
                vehicle.price,
                vehicle.quantity,
            ),
        )

        row = connection.execute(
            "SELECT * FROM vehicles WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return dict(row)


@app.put("/api/vehicles/{vehicle_id}")
def update_vehicle(
    vehicle_id: int,
    vehicle: VehicleCreate,
    admin: dict = Depends(require_admin),
):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE vehicles
            SET make = ?, model = ?, category = ?, price = ?, quantity = ?
            WHERE id = ?
            """,
            (
                vehicle.make,
                vehicle.model,
                vehicle.category,
                vehicle.price,
                vehicle.quantity,
                vehicle_id,
            ),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Vehicle not found",
            )

        row = connection.execute(
            "SELECT * FROM vehicles WHERE id = ?",
            (vehicle_id,),
        ).fetchone()

    return dict(row)


@app.delete("/api/vehicles/{vehicle_id}", status_code=204)
def delete_vehicle(
    vehicle_id: int,
    admin: dict = Depends(require_admin),
):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM vehicles WHERE id = ?",
            (vehicle_id,),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Vehicle not found",
            )


@app.post("/api/vehicles/{vehicle_id}/purchase")
def purchase_vehicle(
    vehicle_id: int,
    current_user: dict = Depends(get_current_user),
):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE vehicles
            SET quantity = quantity - 1
            WHERE id = ? AND quantity > 0
            """,
            (vehicle_id,),
        )

        if cursor.rowcount == 0:
            exists = connection.execute(
                "SELECT id FROM vehicles WHERE id = ?",
                (vehicle_id,),
            ).fetchone()

            if exists is None:
                raise HTTPException(
                    status_code=404,
                    detail="Vehicle not found",
                )

            raise HTTPException(
                status_code=409,
                detail="Vehicle is out of stock",
            )

        row = connection.execute(
            "SELECT * FROM vehicles WHERE id = ?",
            (vehicle_id,),
        ).fetchone()

    return dict(row)


@app.post("/api/vehicles/{vehicle_id}/restock")
def restock_vehicle(
    vehicle_id: int,
    request: RestockRequest,
    admin: dict = Depends(require_admin),
):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE vehicles
            SET quantity = quantity + ?
            WHERE id = ?
            """,
            (request.quantity, vehicle_id),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Vehicle not found",
            )

        row = connection.execute(
            "SELECT * FROM vehicles WHERE id = ?",
            (vehicle_id,),
        ).fetchone()

    return dict(row)

app.mount(
    "/",
    StaticFiles(
        directory=Path(__file__).resolve().parent.parent / "frontend",
        html=True,
    ),
    name="frontend",
)