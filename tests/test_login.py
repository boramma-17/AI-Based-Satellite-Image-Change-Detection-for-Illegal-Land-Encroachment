def test_register_page_loads(client):
    resp = client.get("/register")
    assert resp.status_code == 200


def test_register_creates_user(client):
    resp = client.post("/register", data={
        "username": "alice",
        "email": "alice@example.com",
        "password": "password123",
        "confirm_password": "password123",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Registration successful" in resp.data or b"Login" in resp.data


def test_register_password_mismatch(client):
    resp = client.post("/register", data={
        "username": "bob",
        "email": "bob@example.com",
        "password": "password123",
        "confirm_password": "different123",
    })
    assert b"Passwords do not match" in resp.data


def test_login_success(client, registered_user):
    resp = client.post("/login", data=registered_user, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Welcome back" in resp.data or b"Dashboard" in resp.data


def test_login_wrong_password(client, registered_user):
    resp = client.post("/login", data={
        "email": registered_user["email"],
        "password": "wrongpassword",
    })
    assert b"Invalid email or password" in resp.data


def test_dashboard_requires_login(client):
    resp = client.get("/dashboard", follow_redirects=True)
    assert b"Please log in" in resp.data


def test_logout_clears_session(client, registered_user):
    client.post("/login", data=registered_user)
    resp = client.get("/logout", follow_redirects=True)
    assert resp.status_code == 200
    dashboard_resp = client.get("/dashboard", follow_redirects=True)
    assert b"Please log in" in dashboard_resp.data