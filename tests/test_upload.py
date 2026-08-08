import io
from PIL import Image


def _make_image_bytes(color=(100, 150, 100), size=(64, 64)):
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    buf.seek(0)
    return buf


def _login(client, registered_user):
    client.post("/login", data=registered_user)


def test_upload_requires_login(client):
    resp = client.get("/upload", follow_redirects=True)
    assert b"Please log in" in resp.data


def test_upload_page_loads_when_authenticated(client, registered_user):
    _login(client, registered_user)
    resp = client.get("/upload")
    assert resp.status_code == 200
    assert b"New Detection" in resp.data


def test_upload_rejects_missing_files(client, registered_user):
    _login(client, registered_user)
    resp = client.post("/upload", data={"title": "Test plot"}, follow_redirects=True)
    assert b"select both" in resp.data


def test_upload_accepts_valid_images_and_redirects_to_detection(client, registered_user):
    _login(client, registered_user)
    data = {
        "title": "Plot A",
        "before_image": (_make_image_bytes((50, 50, 50)), "before.png"),
        "after_image": (_make_image_bytes((200, 50, 50)), "after.png"),
    }
    resp = client.post(
        "/upload", data=data, content_type="multipart/form-data", follow_redirects=False
    )
    # Should redirect into the detection-run flow
    assert resp.status_code in (302, 303)
    assert "/detection/" in resp.headers["Location"]