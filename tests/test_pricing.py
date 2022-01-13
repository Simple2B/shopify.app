import pytest

from app import create_app, db
from app.models import Product, Shop
# from app.models import Configuration
from .utils import fill_db_by_test_data
from app.controllers import get_price

# from config import TestingConfig as conf


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True

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


def test_get_price(client):
    product = Product.query.first()
    shop = Shop.query.first()
    price = get_price(product, shop.id)
    assert price
    assert product.price < price

# Site mall of master doesnt work at the moment
# def test_get_price_mom(client):
#     product = Product.query.first()
#     shop = Shop.query.first()
#     Configuration.set_value(shop.id, "MOM_SELECTOR", True)
#     price = get_price(product, shop.id)
#     assert price
#     assert product.price < price
