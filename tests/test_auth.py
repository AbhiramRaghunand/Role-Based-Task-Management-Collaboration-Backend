# tests/test_auth.py


def test_signup_admin(client):
    res = client.post("/signup", json={
        "name": "Admin",
        "email": "admin@test.com",
        "password": "1234",
        "role": "ADMIN"
    })

    assert res.status_code == 201


def test_login_admin(client):
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

    assert res.status_code == 200
    assert "access_token" in res.get_json()["data"]