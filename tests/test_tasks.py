# tests/test_tasks.py
from app.models.user import User
def create_task(client, token, title="Task", description="A"):
    res = client.post(
        "/tasks",
        json={"title": title, "description": description},
        headers={"Authorization": f"Bearer {token}"}
    )
    return res


# ---------------- CREATE ----------------

def test_create_task(client, admin_token):
    res = create_task(client, admin_token, "Test Task", "Testing create")

    assert res.status_code == 201
    data = res.get_json()["data"]
    assert data["title"] == "Test Task"
    assert data["status"] == "PENDING"


# ---------------- VIEW ----------------

def test_view_tasks_basic(client, admin_token):
    create_task(client, admin_token)

    res = client.get(
        "/tasks",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    tasks = res.get_json()["data"]["tasks"]
    assert len(tasks) >= 1


# ---------------- FILTER ----------------

def test_filter_tasks_by_status(client, admin_token):
    create_task(client, admin_token)

    res = client.get(
        "/tasks?status=PENDING",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    tasks = res.get_json()["data"]["tasks"]
    assert all(task["status"] == "PENDING" for task in tasks)


# ---------------- SORT ----------------

def test_sort_tasks_desc(client, admin_token):
    create_task(client, admin_token, "Task1")
    create_task(client, admin_token, "Task2")

    res = client.get(
        "/tasks?sort=created_at&order=desc",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    tasks = res.get_json()["data"]["tasks"]
    assert tasks[0]["id"] >= tasks[1]["id"]


# ---------------- PAGINATION ----------------

def test_pagination(client, admin_token):
    for i in range(3):
        create_task(client, admin_token, f"T{i}")

    res = client.get(
        "/tasks?page=1&limit=1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    tasks = res.get_json()["data"]["tasks"]
    assert len(tasks) == 1


# ---------------- UPDATE STATUS ----------------

def test_update_task_status(client, admin_token):
    res = create_task(client, admin_token, "StatusTask")
    task_id = res.get_json()["data"]["id"]

    res = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "DONE"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 200
    assert res.get_json()["data"]["status"] == "DONE"


# ---------------- ASSIGN ----------------

def test_manager_can_assign_to_team_member(client, manager_token, app):

    # Get manager ID
    with app.app_context():
        manager = User.query.filter_by(email="manager@test.com").first()
        manager_id = manager.id

    # Create team user under manager
    client.post(
        "/signup",
        json={
            "name": "TeamUser",
            "email": "team@test.com",
            "password": "1234",
            "role": "USER",
            "manager_id": manager_id
        }
    )

    # Manager creates the task (IMPORTANT FIX)
    res = create_task(client, manager_token, "AssignTask")
    task_id = res.get_json()["data"]["id"]

    # Fetch user ID
    with app.app_context():
        user = User.query.filter_by(email="team@test.com").first()
        user_id = user.id

    # Manager assigns
    res = client.put(
        f"/tasks/{task_id}/assign",
        json={"user_id": user_id},
        headers={"Authorization": f"Bearer {manager_token}"}
    )

    assert res.status_code == 200


# ---------------- SOFT DELETE ----------------

def test_soft_delete_task(client, admin_token):
    res = create_task(client, admin_token, "DeleteTask")
    task_id = res.get_json()["data"]["id"]

    res = client.delete(
        f"/tasks/{task_id}/delete",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 200


# ---------------- RESTORE ----------------

def test_restore_task(client, admin_token):
    res = create_task(client, admin_token, "RestoreTask")
    task_id = res.get_json()["data"]["id"]

    client.delete(
        f"/tasks/{task_id}/delete",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    res = client.patch(
        f"/tasks/{task_id}/restore",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 200


# ---------------- AUDIT ----------------

def test_audit_log_created(client, admin_token):
    res = create_task(client, admin_token, "AuditTask")
    task_id = res.get_json()["data"]["id"]

    res = client.get(
        f"/tasks/{task_id}/audit",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert res.status_code == 200