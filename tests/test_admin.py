import pytest

from app import db, create_app
from flask import url_for
from .utils import fill_db_by_test_data


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True
    app.config["SERVER_NAME"] = "localhost.localdomain"

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        fill_db_by_test_data()
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def test_all_categories(client):
    response = client.get(url_for("admin.all_categories"))
    assert response.status_code == 200
    assert response.data
