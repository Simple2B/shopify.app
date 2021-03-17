import pytest
from datetime import datetime

from app import db, create_app
from app.models import Product
from app.controllers import scrap
from app.logger import log
from .utils import fill_db_by_test_data


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


def test_scrappy(client, monkeypatch):

    def mockreturn(item_id):
        images = ['https://res.cloudina...783677.jpg', 'https://res.cloudina...837217.jpg']
        return {"item_id": item_id, "qty": len(images), "images": images}
    monkeypatch.setattr(scrap, "scrap_img", mockreturn)
    products = Product.query.limit(10).all()
    assert products
    start_time = datetime.now()
    for prod in products:
        imgs = scrap.scrap_img(prod)
        assert imgs
        log(log.INFO, imgs)
    time_out = datetime.now() - start_time
    log(log.INFO, "Total seconds: [%s] timeout: 10", time_out)
