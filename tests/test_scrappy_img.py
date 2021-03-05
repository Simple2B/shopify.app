import pytest
from datetime import datetime

from app import create_app
from app.models import Product
from app.controllers import scrap
from app.logger import log


@pytest.fixture
def client():
    app = create_app(environment="development")
    app.config["TESTING"] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        yield client
        app_ctx.pop()


def test_scrappy(client):
    products = Product.query.limit(10).all()
    assert products
    start_time = datetime.now()
    for prod in products:
        imgs = scrap.scrap_img(prod.vidaxl_id)
        assert imgs
        log(log.INFO, imgs)
    time_out = datetime.now() - start_time
    log(log.INFO, "Total seconds: [%s] timeout: 10", time_out)
