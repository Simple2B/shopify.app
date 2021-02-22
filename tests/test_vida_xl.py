import pytest
from app.vida_xl import get_products

from app import create_app

@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        yield client
        app_ctx.pop()


def test_get_products(client):
    res = get_products()
    assert res
