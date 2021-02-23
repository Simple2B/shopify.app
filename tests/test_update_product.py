import pytest
import requests

from requests.auth import HTTPBasicAuth

from flask import current_app
from app import create_app
from app.shopify_api import Product
from app.controllers import scrap_img


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        yield client
        app_ctx.pop()


def test_upload_product(client):
    images_src = scrap_img(8).get('images', '')
    assert images_src
    product_api = Product(current_app.config['X_SHOPIFY_ACCESS_TOKEN'], current_app.config['SHOPIFY_DOMAIN'])
    response = product_api.create_product(
            {
                "product": {
                    "title": 'Test_product_2',
                    # "body_html": "<strong>Good snowboard!</strong>",
                    # "vendor": "Burton",
                    "variants": [
                        {
                            # "option1": "First",
                            "inventory_quantity": int(float('1.0')),
                            "price": float('8.8'),
                            # "sku": "123"
                            "presentment_prices": [
                                {
                                    "price": {
                                        "currency_code": 'EUR',
                                        "amount": '8.8'
                                    },
                                    "compare_at_price": None
                                }
                            ],
                            # "updated_at": product['updated_at']
                        }
                    ],
                    "images": [{'src': img_src} for img_src in images_src]
                },
                "status": "active"
            }
        )
    assert response
