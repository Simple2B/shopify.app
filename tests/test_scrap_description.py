import pytest
from app.controllers import scrap_description
from app import create_app, db
from app.models import Product
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


def test_scrap_description(client):
    product = Product.query.first()
    description = scrap_description(product)
    assert description
    assert "This memory foam neck pillow will surely bring you" in description
    product = Product.query.first()
    assert product
    assert product.description == description
