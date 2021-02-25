import requests
from app.shopify_api.base_object import BaseObject

from app.logger import log


class Collection(BaseObject):
    def get_specific_custom_collections(self, *collection_ids: int) -> list:
        collection_ids = ','.join([str(arg) for arg in collection_ids])
        resp = requests.get(
            self.base_url + f"/admin/api/{self.version_api}/custom_collections.json?ids={collection_ids}",
            headers=self.headers
        )
        if resp.status_code == 200:
            custom_collections = resp.json().get("custom_collections", "")
            if custom_collections:
                return custom_collections
            else:
                log(log.DEBUG, "No specific_collections")
        else:
            log(log.ERROR, "Invalid response, status code: [%s]", resp.status_code)

    def create_collection(self, title: str):
        resp = requests.post(
            self.base_url + f"/admin/api/{self.version_api}/custom_collections.json",
            headers=self.headers,
            json={"custom_collection": {"title": title}}
        )
        if resp.status_code == 201:
            return resp.json()
        else:
            log(log.ERROR, "Invalid response, status code: [%s]", resp.status_code)

    def put_product(self, product_id: int, collection_id: int):
        resp = requests.post(
            self.base_url + f"/admin/api/{self.version_api}/collects.json",
            headers=self.headers,
            json={"collect": {"product_id": product_id, "collection_id": collection_id}}
        )
        if resp.status_code == 201:
            return resp.json()
        else:
            log(log.ERROR, "Invalid response, status code: [%s]", resp.status_code)
