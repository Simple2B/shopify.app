import pytest

import shopify

from app import db, create_app
from flask import url_for
from app.models import Shop, Configuration, Category
from .utils import fill_db_by_test_data, CATEGORIES_FILE


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True
    app.config["SERVER_NAME"] = "localhost.localdomain"

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


@pytest.mark.skip
def test_admin(client, monkeypatch):
    def mockreturn(*args, **kwargs):
        return True

    monkeypatch.setattr(shopify.Session, "validate_params", mockreturn)
    shop = Shop.query.first()
    assert shop, "At least one shop must be in the DB"
    response = client.get(url_for("admin.admin", shop_id=shop.id, shop=shop.name))
    assert response
    assert response.status_code == 200
    response = client.post(
        url_for("admin.admin", shop_id=shop.id, shop=shop.name),
        data={"leave_vidaxl_prefix": True},
    )
    assert response.status_code == 302
    assert Configuration.get_value(shop.id, "LEAVE_VIDAXL_PREFIX")
    response = client.post(
        url_for("admin.admin", shop_id=shop.id, shop=shop.name), data={}
    )
    assert response.status_code == 302
    assert not Configuration.get_value(shop.id, "LEAVE_VIDAXL_PREFIX")
    with open(CATEGORIES_FILE, "rb") as file:
        response = client.post(
            url_for("admin.admin", shop_id=shop.id, shop=shop.name),
            data=dict(category_rules_file=file),
        )
        assert response.status_code == 302
    categories = Category.query.all()
    assert len(categories) == 3


def test_all_categories(client):
    response = client.get(url_for("admin.all_categories"))
    assert response.status_code == 200
    assert response.data
