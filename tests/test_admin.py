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


def test_admin2(client):
    shop = Shop.query.first()
    assert shop, "At least one shop must be in the DB"
    response = client.get(url_for("admin.admin", shop_id=shop.id))
    assert response
    assert response.status_code == 200
    response = client.post(url_for("admin.admin", shop_id=shop.id), data={"leave_vidaxl_prefix": True})
    assert response.status_code == 302
    conf = Configuration.query.filter(Configuration.name == "LEAVE_VIDAXL_PREFIX").first()
    assert conf
    assert conf.value == "True"


def test_admin(client):
    Shop(
            name="Test shop name",
            access_token="shpat_5e170as4aeb9dec191c0125caa3a4077",
        ).save()
    configuration = Configuration(
        shop_id=1,
        name='Test conf name',
        value='Some value'
    ).save()
    resp = client.post('/admin/1', data={configuration.name: configuration.value})
    assert resp
    assert b'Admin panel' in resp.data
