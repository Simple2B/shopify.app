import requests

# import json

from requests.auth import HTTPBasicAuth

from flask import current_app
from app.shopify_api import Product
# from app.models import Product
# from app import db
from app.logger import log


def get_documents():
    # headers = {"Authorization": "Basic " + "jamilya.sars@gmail.com" + "ea5d924f-3531-4550-9e28-9ed5cf76d3f7"}

    # current_app.config["AIDAXL_API_BASE_URL"]
    # test url
    sand_box_url = "https://sandbox.b2b.vidaxl.com/"
    # end
    response = requests.get(
        f"{sand_box_url}api_customer/orders/documents",
        auth=HTTPBasicAuth(
            current_app.config["USER_NAME"], current_app.config["API_KEY"]
        ),
    )

    if response.status_code == 200:
        return response.json()
    else:
        return f"Statucs code: {response.status_code}"
    # me_json = response.json()


def update_products(access_token, shopify_url, version_api='2021-01'):
    url = f"{current_app.config['VIDAXL_API_BASE_URL']}/api_customer/products"
    auth = HTTPBasicAuth(current_app.config["USER_NAME"], current_app.config["API_KEY"])
    response = requests.get(f"{url}?offset=0", auth=auth).json()
    total_products = response["pagination"]["total"]

    if total_products:
        product_api = Product(access_token, shopify_url)
        limit = response["pagination"]["limit"]
        products_in_stock = 0
        log(log.DEBUG, "Get total products: [%d]", total_products)
        for product in response.get("data", ""):
            if product["quantity"] == "0.0":
                continue
            else:
                product_api.create_product(
                            {
                                "product": {
                                    "title": product['name'],
                                    # "body_html": "<strong>Good snowboard!</strong>",
                                    # "vendor": "Burton",
                                    "variants": [
                                        {
                                            # "option1": "First",
                                            "inventory_quantity": product['quantity'],
                                            "price": product['price'],
                                            # "sku": "123"
                                            "presentment_prices": [
                                                {
                                                    "price": {
                                                        "currency_code": product['currency'],
                                                        "amount": product['quantity']
                                                    },
                                                    "compare_at_price": None
                                                }
                                            ]
                                        }
                                    ]
                                },
                                "status": "active"
                            }
                        )
                # Product(product_id=product["id"]).save(commit=False)
        range_ = (total_products - limit) // limit
        for i in range(range_ + 1 if (total_products % limit) != 0 else range_):
            try:
                products = (
                    requests.get(f"{url}?offset={limit*(i+1)}", auth=auth)
                    .json()
                    .get("data", "")
                )
            except Exception as err:
                log(log.ERROR, "[%s]", err)
                return f"Value of range: [{i}], range: [{range_}], Exception: {err}"
            if products:
                for product in products:
                    if product["quantity"] == "0.0":
                        continue
                    else:
                        # Product(product_id=product["id"]).save(commit=False)
                        product_api.create_product(
                            {
                                "product": {
                                    "title": product['name'],
                                    # "body_html": "<strong>Good snowboard!</strong>",
                                    # "vendor": "Burton",
                                    "variants": [
                                        {
                                            # "option1": "First",
                                            "inventory_quantity": product['quantity'],
                                            "price": product['price'],
                                            # "sku": "123"
                                            "presentment_prices": [
                                                {
                                                    "price": {
                                                        "currency_code": product['currency'],
                                                        "amount": product['quantity']
                                                    },
                                                    "compare_at_price": None
                                                }
                                            ]
                                        }
                                    ]
                                },
                                "status": "active"
                            }
                        )
                        products_in_stock += 1
        log(log.DEBUG, "Retrive products(%d) which in stock", len(products_in_stock))
        # return json.dumps(products_list)
        # db.session.commit()
        return f"Products in stock: [{len(products_in_stock)}]"
    else:
        log(log.DEBUG, "No products")
        return "No products"
