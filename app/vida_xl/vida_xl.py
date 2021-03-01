import requests

# import json

from requests.auth import HTTPBasicAuth

from flask import current_app
from app.shopify_api import Product, Collection
from app.controllers import upload_product, retry_get_request
from app.logger import log


class VidaXl(object):
    def __init__(self):
        self.basic_auth = HTTPBasicAuth(current_app.config["USER_NAME"], current_app.config["API_KEY"])
        self.base_url = f"{current_app.config['VIDAXL_API_BASE_URL']}/api_customer/products"

    def get_documents(self):
        sand_box_url = "https://sandbox.b2b.vidaxl.com/"
        response = requests.get(
            f"{sand_box_url}api_customer/orders/documents",
            auth=self.basic_auth
        )

        if response.status_code == 200:
            return response.json()
        else:
            return f"Statucs code: {response.status_code}"

    def get_product(self, item_id):
        resp = requests.get(
            f'{self.base_url}?code_eq={item_id}',
            auth=self.basic_auth)
        if not resp.status_code == 200:
            log(log.ERROR, "Invalid response, status code: [%s]", resp.stack_code)
        log(log.DEBUG, f'Response: {resp}')
        return resp.json()

    def update_product(self):
        response = requests.get(f"{self.base_url}?offset=0", auth=self.basic_auth)
        if not response.status_code == 200:
            log(log.ERROR, "Invalid response, status code: [%s]", response.stack_code)
        total_products = response.json()["pagination"]["total"]
        if total_products:
            prod_api = Product()
            collect_api = Collection()
            limit = response["pagination"]["limit"]
            products_in_stock = 0
            log(log.DEBUG, "Get total products: [%d]", total_products)
            products = response.get("data", "")
            for product in products:
                collection = product['category_path'].split('/')[0]
                if products_in_stock >= 100:
                    break
                upload_product(
                        prod_api=prod_api,
                        collect_api=collect_api,
                        product_id=product['id'],
                        collection=collection,
                        title=product['name'],
                        qty=int(float(product['quantity'])),
                        price=float(product['price']),
                    )
                products_in_stock += 1
            if products_in_stock >= 100:  # this code for testing
                return "Memo app (admin)"
            range_ = (total_products - limit) // limit
            for i in range(range_ + 1 if (total_products % limit) != 0 else range_):
                response = retry_get_request(f"{self.base_url}?offset={limit*(i+1)}", auth=self.basic_auth)
                products = response.json().get("data", "")
                for product in products:
                    collection = product['category_path'].split('/')[0]
                    if products_in_stock >= 100:
                        break
                    upload_product(
                        prod_api=prod_api,
                        product_id=product['id'],
                        collect_api=collect_api,
                        collection=collection,
                        title=product['name'],
                        qty=int(float(product['quantity'])),
                        price=float(product['price']),
                    )
                    products_in_stock += 1
                if products_in_stock >= 100:  # this code for testing
                    return "Memo app (admin)"
            log(log.DEBUG, "Retrive products(%d) which in stock", len(products_in_stock))
            # return json.dumps(products_list)
            return f"Products in stock: [{len(products_in_stock)}]"
        else:
            log(log.DEBUG, "No products")
            return "No products"
