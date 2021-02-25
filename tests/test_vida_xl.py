import pytest
import requests

from requests.auth import HTTPBasicAuth
from app.controllers import upload_product, retry_get_request
from app import create_app

from config import TestingConfig as conf


URL = f"{conf.VIDAXL_API_BASE_URL}/api_customer/products"
AUTH = HTTPBasicAuth(conf.USER_NAME, conf.API_KEY)


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        yield client
        app_ctx.pop()


def _test_upload_products(client):
    res = upload_product()
    assert res


def test_get_products(client):
    response = requests.get(f"{URL}?offset=0", auth=AUTH)
    assert response.status_code == 200
    data = response.json().get('data', '')
    assert data


def test_retry_get_request(client):
    for _ in range(100):
        response = retry_get_request(URL, auth=AUTH)
        print(_)
        assert response
