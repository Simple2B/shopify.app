import requests
from app.shopify_api.base_object import BaseObject
from app.logger import log


class Product(BaseObject):
    def get_all(self):
        URL = self.base_url + f"/admin/api/{self.version_api}/products.json"
        resp = requests.get(URL, headers=self.headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            log(log.ERROR, "Response is invalid. Status code: [%s]", resp.status_code)
            raise Exception

    def get_count_products(self):
        req = requests.get(
            self.base_url + f"/admin/api/{self.version_api}/products/count.json"
        )
        return req.json()

    def get_product(self, product_id: int):
        resp = requests.get(
            self.base_url + f"/admin/api/{self.version_api}/products/{product_id}.json",
            headers=self.headers,
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            log(log.ERROR, "Response is invalid. Status code: [%s]", resp.status_code)
            raise Exception

    def set_quantity(self, inventory_item_id: int, quantity: int):
        resp = requests.get(
            self.base_url
            + f"/admin/api/{self.version_api}/inventory_levels.json?inventory_item_ids={inventory_item_id}",
            headers=self.headers,
        )
        if resp.status_code == 200:
            location_id = resp.json()["inventory_levels"][0]["location_id"]
            resp = requests.post(
                self.base_url
                + f"/admin/api/{self.version_api}/inventory_levels/set.json",
                headers=self.headers,
                json={
                    "location_id": location_id,
                    "inventory_item_id": inventory_item_id,
                    "available": quantity,
                },
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                log(
                    log.ERROR,
                    "Response of POST_[%s/admin/api/%s/inventory_levels/adjust.json] is invalid. Status code: [%s]",
                    self.base_url,
                    self.version_api,
                    resp.status_code,
                )
            raise Exception(f"Invalid response code: {resp.staus_code}")
        else:
            log(
                log.ERROR,
                "Response of getting inventory item is invalid. Status code: [%s]",
                resp.status_code,
            )
            raise Exception(f"Invalid response code: {resp.staus_code}")

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
