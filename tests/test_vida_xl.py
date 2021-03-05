import pytest

from requests.auth import HTTPBasicAuth
from app.controllers import download_products
from app import create_app, db
from app.models import Product
from app.vida_xl import VidaXl

from config import TestingConfig as conf


URL = f"{conf.VIDAXL_API_BASE_URL}/api_customer/products"
AUTH = HTTPBasicAuth(conf.VIDAXL_USER_NAME, conf.VIDAXL_API_KEY)


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        # fill_db_by_test_data()
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


@pytest.mark.skipif(not conf.VIDAXL_USER_NAME, reason="VidaXl auth is not configured")
def test_download_products(client):
    LIMIT = 100
    for product in Product.query.all():
        product.delete()
    download_products(LIMIT)
    products = Product.query.all()
    assert products
    assert len(products) == LIMIT
    for prod in products:
        assert prod.is_new
        prod.is_new = False
        prod.save(False)
    products[0].save()
    download_products(LIMIT + LIMIT)
    new_products = Product.query.filter(Product.is_new == True).all()  # noqa E712
    assert new_products
    assert len(new_products) == LIMIT


@pytest.mark.skipif(not conf.VIDAXL_USER_NAME, reason="VidaXl auth is not configured")
def test_download_one_product(client):
    Product.query.delete()
    LIMIT = 1
    download_products(LIMIT)
    vida = VidaXl()
    for product in Product.query.all():
        vida_prod = vida.get_product(product.sku)
        assert vida_prod
