import requests
import json

from requests.auth import HTTPBasicAuth

from flask import current_app
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


def get_products():
    url = f"{current_app.config['VIDAXL_API_BASE_URL']}/api_customer/products"
    auth = HTTPBasicAuth(current_app.config["USER_NAME"], current_app.config["API_KEY"])
    response = requests.get(f"{url}?offset=0", auth=auth).json()
    total_products = response["pagination"]["total"]
    if total_products:
        limit = response["pagination"]["limit"]
        products_list = []
        log(log.DEBUG, "Get total products: [%d]", total_products)
        for product in response.get('data', ''):
            if product['quantity'] == '0.0':
                continue
            else:
                products_list += [product]
        range_ = (total_products - limit) // limit
        for i in range(range_ + 1 if (total_products % limit) != 0 else range_):
            try:
                products = requests.get(f"{url}?offset={limit*(i+1)}", auth=auth).json().get('data', '')
            except Exception as err:
                log.(log.ERROR, "[%s]", err)
                raise Exception((f'Value of range: [{i}], range: [{range_}]'))
            if products:
                for product in products:
                    if product['quantity'] == '0.0':
                        continue
                    else:
                        products_list += [product]
        log(log.DEBUG, "Retrive products(%d) which in stock", len(products_list))
        return json.dumps(products_list)
    else:
        log(log.DEBUG, "No products")
        return "No products"
