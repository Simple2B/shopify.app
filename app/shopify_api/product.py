import requests


class Product:

    def __init__(self, access_token, url: str, version_api='2021-01'):
        self.url = url
        self.version_api = version_api
        # self.headers = {"X-Shopify-Access-Token": "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"}
        self.headers = {"X-Shopify-Access-Token": access_token}

    def get_all(self):
        req = requests.get(self.url + f'/admin/api/{self.version_api}/products.json', headers=self.headers)
        return req.json()

    def get_count_products(self):
        req = requests.get(self.url + f'/admin/api/{self.version_api}/products/count.json')
        return req.json()

    def get_product(self, product_id):
        req = requests.get(self.url + f'/admin/api/{self.version_api}/products/{product_id}.json', headers=self.headers)
        return req.json()

    def create_product(self, data: dict):
        req = requests.post(self.url + f'/admin/api/{self.version_api}/products.json', headers=self.headers, json=data)
        return req.json()

    def update_product(self, product_id, data):
        req = requests.put(self.url + f'/admin/api/2021-01/products/{product_id}.json', data=data)
        return req.json()

    def delete_product(self, product_id):
        req = requests.delete(self.url + f'/admin/api/2021-01/products/{product_id}.json')
        return req.json()
