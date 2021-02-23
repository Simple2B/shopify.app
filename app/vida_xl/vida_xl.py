import requests

# import json

from requests.auth import HTTPBasicAuth

from flask import current_app
from app.shopify_api import Product, Collection
from app.controllers import update_product
from app.logger import log


def get_documents():
    sand_box_url = "https://sandbox.b2b.vidaxl.com/"
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


def update_products():
    url = f"{current_app.config['VIDAXL_API_BASE_URL']}/api_customer/products"
    auth = HTTPBasicAuth(current_app.config["USER_NAME"], current_app.config["API_KEY"])
    response = requests.get(f"{url}?offset=0", auth=auth).json()
    total_products = response["pagination"]["total"]

    if total_products:
        prod_api = Product()
        collect_api = Collection()
        limit = response["pagination"]["limit"]
        products_in_stock = 0
        log(log.DEBUG, "Get total products: [%d]", total_products)
        products = response.get("data", "")
        for product in products:
            collection = product['category_path'].split('/')[0]
            if products_in_stock >= 50:
                break
            update_product(
                    prod_api=prod_api,
                    collect_api=collect_api,
                    prod_id=product['id'],
                    collection=collection,
                    title=product['name'],
                    qty=int(float(product['quantity'])),
                    price=float(product['price']),
                    currency=product['currency']
                )
            products_in_stock += 1
        if products_in_stock >= 50:  # this code for testing
            return "Memo app (admin)"
        range_ = (total_products - limit) // limit
        for i in range(range_ + 1 if (total_products % limit) != 0 else range_):
            try:
                response = requests.get(f"{url}?offset={limit*(i+1)}", auth=auth)
            except Exception as err:
                log(log.ERROR, "Exception: [%s]", err)
                while response.status_code != 200:
                    response = requests.get(f"{url}?offset={limit*(i+1)}", auth=auth)
                products = response.json().get("data", "")
            for product in products:
                collection = product['category_path'].split('/')[0]
                if products_in_stock >= 50:
                    break
                update_product(
                    prod_api=prod_api,
                    prod_id=product['id'],
                    collect_api=collect_api,
                    collection=collection,
                    title=product['name'],
                    qty=int(float(product['quantity'])),
                    price=float(product['price']),
                    currency=product['currency']
                )
                products_in_stock += 1
            if products_in_stock >= 50:  # this code for testing
                return "Memo app (admin)"
        log(log.DEBUG, "Retrive products(%d) which in stock", len(products_in_stock))
        # return json.dumps(products_list)
        return f"Products in stock: [{len(products_in_stock)}]"
    else:
        log(log.DEBUG, "No products")
        return "No products"
