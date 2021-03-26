from sqlalchemy import or_
from app.models.configuration import Configuration
import pytest

from app import create_app, db
from app.models import Shop
from .utils import fill_db_by_test_data
from app.controllers import reset
from app.controllers.categories import PARAMETERS


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


def test_reset_config(client):
    shop = Shop.query.first()
    configs = Configuration.query.filter(Configuration.shop_id == shop.id).filter(
        or_(Configuration.name == v for v in PARAMETERS)).all()
    assert configs
    reset(shop.id)
    configs = Configuration.query.filter(Configuration.shop_id == shop.id).filter(
        or_(Configuration.name == v for v in PARAMETERS)).all()
    assert not configs
