# tests/test_tasks.py


def test_create_task(client, login):
    headers = login()
    resp = client.post(
        "/tasks", json={"title": "Buy milk", "description": "2 litres"}, headers=headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Buy milk"
    assert body["description"] == "2 litres"
    assert body["is_done"] is False
    assert body["id"] > 0


def test_create_task_rejects_empty_title(client, login):
    resp = client.post("/tasks", json={"title": ""}, headers=login())
    assert resp.status_code == 422


def test_create_task_requires_auth(client):
    resp = client.post("/tasks", json={"title": "Nope"})
    assert resp.status_code == 401


def test_list_tasks_returns_only_own_tasks(client, login):
    alice = login("alice@example.com")
    bob = login("bob@example.com")
    client.post("/tasks", json={"title": "Alice task"}, headers=alice)
    client.post("/tasks", json={"title": "Bob task"}, headers=bob)

    resp = client.get("/tasks", headers=alice)
    titles = [t["title"] for t in resp.json()]
    assert titles == ["Alice task"]


def test_list_tasks_pagination(client, login):
    headers = login()
    for i in range(5):
        client.post("/tasks", json={"title": f"Task {i}"}, headers=headers)

    page1 = client.get("/tasks?limit=2&skip=0", headers=headers).json()
    page2 = client.get("/tasks?limit=2&skip=2", headers=headers).json()
    assert [t["title"] for t in page1] == ["Task 0", "Task 1"]
    assert [t["title"] for t in page2] == ["Task 2", "Task 3"]


def test_list_tasks_rejects_limit_over_100(client, login):
    resp = client.get("/tasks?limit=101", headers=login())
    assert resp.status_code == 422


def test_list_tasks_filter_by_is_done(client, login):
    headers = login()
    t1 = client.post("/tasks", json={"title": "Open"}, headers=headers).json()
    t2 = client.post("/tasks", json={"title": "Finished"}, headers=headers).json()
    client.patch(f"/tasks/{t2['id']}", json={"is_done": True}, headers=headers)

    done = client.get("/tasks?is_done=true", headers=headers).json()
    not_done = client.get("/tasks?is_done=false", headers=headers).json()
    assert [t["title"] for t in done] == ["Finished"]
    assert [t["title"] for t in not_done] == ["Open"]


def test_get_single_task(client, login):
    headers = login()
    created = client.post("/tasks", json={"title": "Read me"}, headers=headers).json()
    resp = client.get(f"/tasks/{created['id']}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Read me"


def test_get_missing_task_returns_404(client, login):
    resp = client.get("/tasks/9999", headers=login())
    assert resp.status_code == 404


def test_patch_updates_only_sent_fields(client, login):
    headers = login()
    created = client.post(
        "/tasks", json={"title": "Original", "description": "Keep me"}, headers=headers
    ).json()

    resp = client.patch(f"/tasks/{created['id']}", json={"is_done": True}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_done"] is True
    assert body["title"] == "Original"          # untouched
    assert body["description"] == "Keep me"     # untouched


def test_delete_task(client, login):
    headers = login()
    created = client.post("/tasks", json={"title": "Temp"}, headers=headers).json()

    assert client.delete(f"/tasks/{created['id']}", headers=headers).status_code == 204
    assert client.get(f"/tasks/{created['id']}", headers=headers).status_code == 404


# ---------- Authorization: the important ones ----------

def test_user_cannot_read_another_users_task(client, login):
    alice = login("alice@example.com")
    bob = login("bob@example.com")
    task = client.post("/tasks", json={"title": "Private"}, headers=alice).json()

    resp = client.get(f"/tasks/{task['id']}", headers=bob)
    assert resp.status_code == 404


def test_user_cannot_update_another_users_task(client, login):
    alice = login("alice@example.com")
    bob = login("bob@example.com")
    task = client.post("/tasks", json={"title": "Private"}, headers=alice).json()

    resp = client.patch(f"/tasks/{task['id']}", json={"title": "Hacked"}, headers=bob)
    assert resp.status_code == 404
    # and the original is unchanged
    still = client.get(f"/tasks/{task['id']}", headers=alice).json()
    assert still["title"] == "Private"


def test_user_cannot_delete_another_users_task(client, login):
    alice = login("alice@example.com")
    bob = login("bob@example.com")
    task = client.post("/tasks", json={"title": "Private"}, headers=alice).json()

    resp = client.delete(f"/tasks/{task['id']}", headers=bob)
    assert resp.status_code == 404
    assert client.get(f"/tasks/{task['id']}", headers=alice).status_code == 200