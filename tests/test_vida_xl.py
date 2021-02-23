import pytest
import requests

from requests.auth import HTTPBasicAuth
from app.vida_xl import update_products
from flask import current_app

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


def test_update_products(client):
    res = update_products()
    assert res


def test_get_products(client):
    url = f"{current_app.config['VIDAXL_API_BASE_URL']}/api_customer/products"
    auth = HTTPBasicAuth(current_app.config["USER_NAME"], current_app.config["API_KEY"])
    response = requests.get(f"{url}?offset=0", auth=auth)
    assert response.status_code == 200
    data = response.json().get('data', '')
    assert data
