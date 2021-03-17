import pytest

from app import create_app, db
from app.models import Shop
from .utils import fill_db_by_test_data
from app.controllers import get_categories_configuration_tree, apply_categories_configuration_tree

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


def test_config_tree(client):
    shop = Shop.query.first()
    data = get_categories_configuration_tree(shop.id)
    assert data
    data["nodes"][0]["nodes"][0]["MARGIN_PERCENT"] = 555
    apply_categories_configuration_tree(shop.id, data)
    data = get_categories_configuration_tree(shop.id)
    assert data
    assert data["nodes"][0]["nodes"][0]["MARGIN_PERCENT"] == 555

    apply_categories_configuration_tree(shop.id, None)
    apply_categories_configuration_tree(shop.id, {})
