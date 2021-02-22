import requests
from flask import current_app as app
from app.logger import log


class Product:
    """All product methods in Shopify API"""

    VERSION_API_URL = app.config["VERISION_API_URL"]

    def __init__(self, url: str) -> None:
        self.url = url

    def get_all(self):
        try:
            req = requests.get(self.url + self.VERSION_API_URL + '/products.json')
        except Exception as e:
            log(log.ERROR, 'Invalid response: [%s]', e)
        return req.json()

    def get_count_products(self):
        try:
            req = requests.get(self.url + self.VERSION_API_URL + '/products/count.json')
        except Exception as e:
            log(log.ERROR, 'Invalid response: [%s]', e)
        return req.json()

    def get_product(self, product_id):
        try:
            req = requests.get(self.url + self.VERSION_API_URL + f'/products/{product_id}.json')
        except Exception as e:
            log(log.ERROR, 'Invalid response: [%s]', e)
        return req.json()

    def create_product(self, data):
        try:
            req = requests.post(self.url + self.VERSION_API_URL + '/products.json', data=data)
        except Exception as e:
            log(log.ERROR, 'Invalid response: [%s]', e)
        return req.json()

    def update_product(self, product_id, data):
        try:
            req = requests.put(self.url + self.VERSION_API_URL + f'/products/{product_id}.json', data=data)
        except Exception as e:
            log(log.ERROR, 'Invalid response: [%s]', e)
        return req.json()

    def delete_product(self, product_id):
        try:
            req = requests.delete(self.url + self.VERSION_API_URL + f'/products/{product_id}.json')
        except Exception as e:
            log(log.ERROR, 'Invalid response: [%s]', e)
        return req.json()
