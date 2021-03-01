import pytest

from app import db, create_app
from app.models import Shop, Configuration


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
