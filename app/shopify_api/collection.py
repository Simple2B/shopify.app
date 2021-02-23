import requests
from app.shopify_api.base_object import BaseObject


from app.logger import log


class Collection(BaseObject):
    def create_collection(self, data: dict):
        resp = requests.post(
            self.base_url + f"/admin/api/{self.version_api}/custom_collections.json",
            headers=self.headers,
            json=data
        )
        if resp.status_code == 201:
            return resp.json().get('custom_collection', '')['id']
        else:
            log(log.ERROR, "Invalid response, status code: [%s]", resp.status_code)

    def put_product(self, data: dict):
        resp = requests.post(
            self.base_url + f"/admin/api/{self.version_api}/collects.json",
            headers=self.headers,
            json=data
        )
        if resp.status_code == 201:
            return resp.json()
        else:
            log(log.ERROR, "Invalid response, status code: [%s]", resp.status_code)
