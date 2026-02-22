# tests/test_roles.py

def test_admin_can_access_protected_route(client, admin_token):
    res = client.get(
        "/userslist",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 200


def test_user_cannot_access_admin_route(client, user_token):
    res = client.get(
        "/userslist",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert res.status_code in (403,404)