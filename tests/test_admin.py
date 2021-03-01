import pytest

from app import db, create_app
from flask import url_for
from app.models import Shop, Configuration
from .utils import fill_db_by_test_data


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True
    app.config["SERVER_NAME"] = "localhost"

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


def test_admin(client):
    shop = Shop.query.first()
    assert shop, "At least one shop must be in the DB"
    response = client.get(url_for("admin.admin", shop_id=shop.id))
    assert response
    assert response.status_code == 200
    response = client.post(url_for("admin.admin", shop_id=shop.id), data={"leave_vidaxl_prefix": True})
    assert response.status_code == 302
    assert Configuration.get_value(shop.id, "LEAVE_VIDAXL_PREFIX")
    response = client.post(url_for("admin.admin", shop_id=shop.id), data={})
    assert response.status_code == 302
    assert not Configuration.get_value(shop.id, "LEAVE_VIDAXL_PREFIX")
