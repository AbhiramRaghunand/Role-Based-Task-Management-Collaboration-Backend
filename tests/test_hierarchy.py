from app.models.user import User


def test_manager_cannot_assign_outside_team(client, admin_token, manager_token, app):

    # Step 1: Create a task (by admin)
    task_res = client.post(
        "/tasks",
        json={"title": "Test Task", "description": "A"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert task_res.status_code == 201
    task_id = task_res.get_json()["data"]["id"]

    # Step 2: Create another MANAGER under admin
    other_manager_res = client.post(
        "/signup",
        json={
            "name": "OtherManager",
            "email": "other_manager@test.com",
            "password": "1234",
            "role": "MANAGER"
        }
    )
    assert other_manager_res.status_code == 201

    # Fetch other manager id
    with app.app_context():
        other_manager = User.query.filter_by(email="other_manager@test.com").first()
        other_manager_id = other_manager.id

    # Step 3: Create USER under other manager
    signup_res = client.post(
        "/signup",
        json={
            "name": "OtherUser",
            "email": "other@test.com",
            "password": "1234",
            "role": "USER",
            "manager_id": other_manager_id
        }
    )
    assert signup_res.status_code == 201

    # Fetch created user
    with app.app_context():
        user = User.query.filter_by(email="other@test.com").first()
        user_id = user.id

    # Step 4: Manager 1 tries assigning outside team
    res = client.put(
        f"/tasks/{task_id}/assign",
        json={"user_id": user_id},
        headers={"Authorization": f"Bearer {manager_token}"}
    )

    assert res.status_code in (400, 403)