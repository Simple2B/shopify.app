import pytest

from app import db, create_app


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def test_remove_vidaxl_text(client):
    resp = client.post('/remove_vidaxl_text', data={'check_box': True})
    assert resp
    assert b'checked' in resp.data
