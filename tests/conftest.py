# tests/conftest.py

import pytest
from app import create_app
from app.extensions import db
from app.models.user import User


@pytest.fixture
def app():
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# -----------------------------
# ADMIN FIXTURE
# -----------------------------
@pytest.fixture
def admin_token(client):
    # Create ADMIN (no manager required)
    client.post("/signup", json={
        "name": "Admin",
        "email": "admin@test.com",
        "password": "1234",
        "role": "ADMIN"
    })

    res = client.post("/login", json={
        "email": "admin@test.com",
        "password": "1234"
    })

    return res.get_json()["data"]["access_token"]


# -----------------------------
# MANAGER FIXTURE
# -----------------------------
@pytest.fixture
def manager_token(client, admin_token, app):
    # Create MANAGER
    client.post("/signup", json={
        "name": "Manager",
        "email": "manager@test.com",
        "password": "1234",
        "role": "MANAGER"
    })

    res = client.post("/login", json={
        "email": "manager@test.com",
        "password": "1234"
    })

    return res.get_json()["data"]["access_token"]


# -----------------------------
# USER FIXTURE (REQUIRES MANAGER)
# -----------------------------
@pytest.fixture
def user_token(client, manager_token, app):
    with app.app_context():
        manager = User.query.filter_by(email="manager@test.com").first()
        manager_id = manager.id

    client.post("/signup", json={
        "name": "User",
        "email": "user@test.com",
        "password": "1234",
        "role": "USER",
        "manager_id": manager_id
    })

    res = client.post("/login", json={
        "email": "user@test.com",
        "password": "1234"
    })

    return res.get_json()["data"]["access_token"]