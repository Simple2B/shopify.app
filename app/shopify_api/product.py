import requests
from app.shopify_api.base_object import BaseObject


class Product(BaseObject):
    def get_all(self):
        req = requests.get(
            self.base_url + f"/admin/api/{self.version_api}/products.json",
            headers=self.headers,
        )
        return req.json()

    def get_count_products(self):
        req = requests.get(
            self.base_url + f"/admin/api/{self.version_api}/products/count.json"
        )
        return req.json()

    def get_product(self, product_id):
        req = requests.get(
            self.base_url + f"/admin/api/{self.version_api}/products/{product_id}.json",
            headers=self.headers,
        )
        return req.json()

    def create_product(self, data: dict):
        resp = requests.post(
            self.base_url + f"/admin/api/{self.version_api}/products.json",
            headers=self.headers,
            json=data,
        )
        if resp.status_code == 201:
            return resp.json()
        else:
            return "Response is not valid"

    def update_product(self, product_id, data):
        req = requests.put(
            self.base_url + f"/admin/api/2021-01/products/{product_id}.json", data=data
        )
        return req.json()

    def delete_product(self, product_id):
        req = requests.delete(
            self.base_url + f"/admin/api/2021-01/products/{product_id}.json"
        )
        return req.json()
