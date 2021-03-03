import requests
from app.shopify_api.base_object import ShopifyBase

from app.logger import log


class Collection(ShopifyBase):

    def __init__(self, shop_id, collection_id, data):
        self.shop_id = shop_id
        self.collection_id = collection_id
        self.data = data

    def get_specific_custom_collections(self, *collection_ids: int) -> list:
        collection_ids = ','.join([str(arg) for arg in collection_ids])
        resp = requests.get(
            self.BASE_URL + f"/admin/api/{self.VERSION_API}/custom_collections.json?ids={collection_ids}",
            headers=self.headers(self.shop_id)
        )
        if resp.status_code == 200:
            custom_collections = resp.json().get("custom_collections", "")
            if custom_collections:
                return custom_collections
            else:
                log(log.DEBUG, "No specific_collections")
        else:
            log(log.ERROR, "Invalid response, status code: [%s]", resp.status_code)

    @classmethod
    def create(cls, title: str, shop_id: int):
        resp = requests.post(
            cls.BASE_URL + f"/admin/api/{cls.VERSION_API}/custom_collections.json",
            headers=cls.headers(cls.shop_id),
            json={"custom_collection": {"title": title}}
        )
        if resp.status_code != 201:
            log(log.ERROR, "Invalid response, status code: [%s]", resp.status_code)
            return None
        return cls(shop_id, resp.json())

    def put_product(cls, product_id: int, collection_id: int):
        resp = requests.post(
            cls.BASE_URL + f"/admin/api/{cls.VERSION_API}/collects.json",
            headers=cls.headers(cls.shop_id),
            json={"collect": {"product_id": product_id, "collection_id": collection_id}}
        )
        if resp.status_code == 201:
            return resp.json()
        elif resp.status_code == 422:
            log(log.DEBUG, "Product [id:%d] already exists in this collection", product_id)
            return resp
        else:
            log(log.ERROR, "Invalid response, status code: [%s]", resp.status_code)
