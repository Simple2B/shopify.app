import pytest

from app import create_app
from app.shopify_api import Product, Collection
from app.controllers import scrap_img
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


# Product
@pytest.mark.skip
def test_get_products(client):
    products = Product().get_all()
    assert products
    assert products['products'][0]


@pytest.mark.skip
def test_get_product(client):
    res = Product().get_product(6053512642766)
    assert res


@pytest.mark.skip
def test_set_quantity_to_product(client):
    json_data = Product().set_quantity(inventory_item_id=39525202821326, quantity=15)
    assert json_data


@pytest.mark.skip
def test_create_product(client):
    images_src = scrap_img(8).get('images', '')
    assert images_src
    product_api = Product()
    response = product_api.create_product(
            {
                "product": {
                    "title": 'Test_product_2',
                    "variants": [
                        {
                            "inventory_quantity": int(float('1.0')),
                            "price": float('8.8'),
                            "presentment_prices": [
                                {
                                    "price": {
                                        "currency_code": 'EUR',
                                        "amount": '8.8'
                                    },
                                    "compare_at_price": None
                                }
                            ],
                        }
                    ],
                    "images": [{'src': img_src} for img_src in images_src]
                },
                "status": "active"
            }
        )
    assert response


# Collection
@pytest.mark.skip
def test_create_collection(client):
    res = Collection().create_collection(title="Some Test Collection")
    assert res
    collection_id = res.get('custom_collection', '')['id']
    assert collection_id


@pytest.mark.skip
def test_put_product_to_collection(client):
    collection = Collection()
    # res = collection.get_specific_custom_collections(260457595086)
    res = collection.get_specific_custom_collections(235229774030)
    assert res
    collection_id = res[0]['id']
    assert collection_id
    if 235229774030 == collection_id:
        # res = collection.put_product(6053512642766, 260457595086)
        res = collection.put_product(6053512642766, 235229774030)
        if res.status_code == 422:
            assert b'product_id":["already exists in this collection' in res.content
        else:
            assert res
    else:
        log(log.WARNING, "Collection did not find")
